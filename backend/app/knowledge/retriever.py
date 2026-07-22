"""Hybrid retriever: tag filtering + ChromaDB semantic search + MMR rerank."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import ClassVar, List, Optional, Sequence

import numpy as np
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from .embedder import KBEmbedder
from .loader import KnowledgeBaseLoader
from .schemas import MethodCard, Paper, Problem, Template


class HybridRetriever(BaseRetriever):
    """Combines tag-based filtering with vector similarity search and MMR reranking.

    Retrieval pipeline:
    1. Vector similarity search (with optional metadata filter)  → fetch_k candidates
    2. MMR rerank (diversity-aware)                              → deduplicate & diversify
    3. Tag-based filtering (complementary, for cold-start cases)  → merge & deduplicate
    4. Score normalization                                       → stable ordering
    """

    TAG_MATCH_SCORE: ClassVar[float] = 0.85  # fixed relevance score for tag-based matches

    # BaseRetriever 是 pydantic 模型，字段必须先声明才能赋值
    embedder: KBEmbedder
    loader: KnowledgeBaseLoader
    _vector_store: Optional[object] = None

    def __init__(
        self,
        kb_root: Path,
        persist_dir: Path,
        embedding_provider: str = "openai",
    ):
        super().__init__(
            embedder=KBEmbedder(kb_root, persist_dir, embedding_provider),
            loader=KnowledgeBaseLoader(kb_root),
        )

    # ── lazy init ──────────────────────────────────────────────────────

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = self.embedder.load_existing()
        return self._vector_store

    # ── public API ─────────────────────────────────────────────────────

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        metadata_filter: Optional[dict] = None,
    ) -> List[tuple[Document, float]]:
        """Vector similarity search returning (document, distance_score) tuples.

        Lower distance = more relevant.  Scores are L2 distances from ChromaDB.
        """
        search_kwargs: dict = {"k": k}
        if metadata_filter:
            search_kwargs["filter"] = metadata_filter

        return self.vector_store.similarity_search_with_score(
            query, k=k, filter=metadata_filter
        )

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        metadata_filter: Optional[dict] = None,
    ) -> List[Document]:
        """Vector similarity search without scores."""
        return self.vector_store.similarity_search(
            query, k=k, filter=metadata_filter
        )

    # ── BaseRetriever override ─────────────────────────────────────────

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        **kwargs,
    ) -> List[Document]:
        """Core retrieval: vector search → MMR → tag merge.

        Keyword Args:
            problem_type:       Tag filter (optimization / prediction / evaluation / ...).
            metadata_filter:    ChromaDB where-clause dict, e.g. {"type": "paper"}.
            k:                  Final result count (default 5).
            fetch_k:            Candidates fetched before MMR (default 20, must be >= k).
            use_mmr:            Enable MMR diversification (default True).
            mmr_lambda:         Relevance-vs-diversity trade-off (0-1, default 0.5).
        """
        k = kwargs.get("k", 5)
        fetch_k = kwargs.get("fetch_k", max(k * 4, 20))
        use_mmr = kwargs.get("use_mmr", True)
        mmr_lambda = kwargs.get("mmr_lambda", 0.5)
        problem_type = kwargs.get("problem_type")
        metadata_filter = kwargs.get("metadata_filter")

        # 1. Vector search (fetch more than needed for MMR pool)
        scored: List[tuple[Document, float]] = []
        try:
            scored = self.similarity_search_with_score(
                query, k=max(fetch_k, k), metadata_filter=metadata_filter
            )
        except Exception:
            # ChromaDB may not be built yet — fall back to tag-only
            pass

        # 2. MMR rerank
        if use_mmr and len(scored) > k:
            docs = self._mmr_rerank(
                query, scored, k=k, lam=mmr_lambda
            )
        else:
            docs = [doc for doc, _ in scored[:k]]
            for doc, score in scored[:k]:
                doc.metadata["score"] = self._normalize_chroma_score(score)

        # 2.5 向量索引不可用或无结果时的关键词兜底（YAML 全量子串匹配）
        if not docs:
            docs = self._keyword_search(query, k)

        # 3. Tag-based complementary results (for cold-start / edge cases)
        tag_docs = self._filter_by_tags(problem_type, k)

        # 4. Merge: tag first (deterministic), then vector (deduplicated by id)
        return self._merge_results(tag_docs, docs, k)

    # ── MMR ────────────────────────────────────────────────────────────

    @staticmethod
    def _mmr_rerank(
        query: str,
        scored_docs: List[tuple[Document, float]],
        k: int = 5,
        lam: float = 0.5,
    ) -> List[Document]:
        """Maximum Marginal Relevance reranking.

        lam=1.0 → pure relevance;  lam=0.0 → pure diversity.
        ChromaDB returns L2 *distance* (lower = better), so we invert to similarity.
        """
        if not scored_docs:
            return []

        docs = [d for d, _ in scored_docs]
        # Invert L2 distance to similarity score [0, 1]
        distances = np.array([s for _, s in scored_docs], dtype=np.float64)
        sims = 1.0 / (1.0 + distances)  # [0, 1]
        sims = sims / (sims.max() + 1e-8)  # normalize

        # Pairwise cosine similarity of document embeddings (approximated via page_content)
        # For a proper implementation we'd re-embed, but this lightweight heuristic
        # penalises docs with identical content and rewards diversity of coverage.
        n = len(docs)
        pairwise = np.eye(n, dtype=np.float64)
        for i in range(n):
            for j in range(i + 1, n):
                # Simple Jaccard-like overlap of token sets as diversity proxy
                ti = set(docs[i].page_content.split())
                tj = set(docs[j].page_content.split())
                if not ti or not tj:
                    pairwise[i, j] = pairwise[j, i] = 0.0
                    continue
                pairwise[i, j] = pairwise[j, i] = len(ti & tj) / len(ti | tj)

        selected: List[int] = []
        remaining = list(range(n))

        for _ in range(min(k, n)):
            if not remaining:
                break

            if not selected:
                # First pick: highest relevance
                best = max(remaining, key=lambda j: sims[j])
            else:
                # MMR: λ*relevance - (1-λ)*max_similarity_to_selected
                def mmr_score(j: int) -> float:
                    rel = sims[j]
                    div_penalty = max(pairwise[j, s] for s in selected)
                    return lam * rel - (1.0 - lam) * div_penalty

                best = max(remaining, key=mmr_score)

            selected.append(best)
            remaining.remove(best)

        result = []
        for idx in selected:
            doc = docs[idx]
            doc.metadata["score"] = round(float(sims[idx]), 4)
            result.append(doc)
        return result

    @staticmethod
    def _normalize_chroma_score(distance: float) -> float:
        """Convert ChromaDB L2 distance to a [0, 1] similarity score."""
        return round(1.0 / (1.0 + float(distance)), 4)

    # ── tag filtering ──────────────────────────────────────────────────

    def _filter_by_tags(
        self, problem_type: Optional[str], k: int
    ) -> List[Document]:
        """Exact-match tag filtering: returns complete documents with scores."""
        if not problem_type:
            return []

        results: List[Document] = []

        # Method cards
        cards = self.loader.get_methods_by_category(problem_type)
        for card in cards[:k]:
            doc = self._card_to_document(card)
            doc.metadata["score"] = self.TAG_MATCH_SCORE
            results.append(doc)

        # Papers
        papers = self.loader.get_papers_by_type(problem_type)
        for paper in papers[:k]:
            doc = self._paper_to_document(paper)
            doc.metadata["score"] = self.TAG_MATCH_SCORE
            results.append(doc)

        # Templates
        templates = self.loader.get_templates_for_type(problem_type)
        for tpl in templates[:k]:
            doc = self._template_to_document(tpl)
            doc.metadata["score"] = self.TAG_MATCH_SCORE
            results.append(doc)

        # Problems
        problems = self.loader.get_problems_by_type(problem_type)
        for prob in problems[:k]:
            doc = self._problem_to_document(prob)
            doc.metadata["score"] = self.TAG_MATCH_SCORE
            results.append(doc)

        return results

    # ── keyword fallback (no embeddings required) ─────────────────────

    def _keyword_search(self, query: str, k: int) -> List[Document]:
        """关键词子串匹配兜底：向量索引不可用（未构建/无 Key）时保证基础可检索。"""
        q = query.strip().lower()
        if not q:
            return []
        terms = [t for t in q.split() if t] or [q]

        def score(text: str) -> float:
            t = text.lower()
            hits = sum(1 for term in terms if term in t)
            if hits == 0:
                return 0.0
            s = hits / len(terms)
            if q in t:
                s += 0.5
            return s

        candidates: List[tuple[Document, float]] = []

        for card in self.loader.load_all_methods():
            text = " ".join([
                card.name, card.principle or "",
                " ".join(card.category or []),
                " ".join(card.applicable_when or []),
                " ".join(card.typical_scenarios or []),
            ])
            s = score(text)
            if s > 0:
                candidates.append((self._card_to_document(card), s))

        for paper in self.loader.load_all_papers():
            text = " ".join([
                paper.title, str(paper.year), paper.competition or "",
                paper.analysis.problem_summary if paper.analysis else "",
                " ".join(paper.tags.get("problem_type", []) or []),
                " ".join(paper.tags.get("core_models", []) or []),
            ])
            s = score(text)
            if s > 0:
                candidates.append((self._paper_to_document(paper), s))

        for tpl in self.loader.load_all_templates():
            text = " ".join([
                tpl.name, " ".join(tpl.applicable_to or []),
                " ".join(step.name for step in (tpl.steps or [])),
            ])
            s = score(text)
            if s > 0:
                candidates.append((self._template_to_document(tpl), s))

        for prob in self.loader.load_all_problems():
            text = " ".join([
                prob.title, str(prob.year), prob.competition or "",
                prob.background or "",
                " ".join(prob.objectives or []),
                " ".join(prob.tags.get("problem_type", []) or []),
            ])
            s = score(text)
            if s > 0:
                candidates.append((self._problem_to_document(prob), s))

        candidates.sort(key=lambda x: x[1], reverse=True)
        out: List[Document] = []
        for doc, s in candidates[:k]:
            # 关键词匹配置信度低于 tag(0.85) 与向量，但保证可用
            doc.metadata["score"] = min(0.5 + 0.3 * s, 0.9)
            out.append(doc)
        return out

    # ── document builders (rich page_content for tag results) ──────────

    @staticmethod
    def _card_to_document(card: MethodCard) -> Document:
        parts = [card.principle]
        if card.typical_scenarios:
            parts.append("适用场景: " + "; ".join(card.typical_scenarios))
        if card.applicable_when:
            parts.append("适用条件: " + "; ".join(card.applicable_when))
        if card.not_applicable_when:
            parts.append("不适用条件: " + "; ".join(card.not_applicable_when))
        if card.common_mistakes:
            parts.append(
                "常见误用: "
                + "; ".join(m.mistake for m in card.common_mistakes)
            )
        if card.code_snippets:
            parts.append(
                "代码示例: "
                + "\n".join(
                    f"```{cs.language}\n{cs.code}\n```"
                    for cs in card.code_snippets
                )
            )
        return Document(
            page_content="\n".join(parts),
            metadata={
                "type": "method_card",
                "id": card.id,
                "name": card.name,
                "categories": card.category,
                "related_cards": card.related_cards,
                "related_papers": card.related_papers,
            },
        )

    @staticmethod
    def _paper_to_document(paper: Paper) -> Document:
        parts = [
            f"题目: {paper.title}",
            f"年份: {paper.year} | 竞赛: {paper.competition} | 赛题: {paper.problem_id}",
            f"问题类型: {paper.tags.get('problem_type', [])}",
            f"核心模型: {paper.tags.get('core_models', [])}",
            f"问题概述: {paper.analysis.problem_summary}",
            f"建模思路: {paper.model.approach}",
            f"创新点: {paper.model.innovation}",
            f"求解方法: {paper.model.solution_method}",
            f"可学之处: {paper.evaluation.lessons}",
        ]
        if paper.analysis.key_assumptions:
            parts.append("关键假设: " + "; ".join(paper.analysis.key_assumptions))
        if paper.evaluation.strengths:
            parts.append("优点: " + "; ".join(paper.evaluation.strengths))
        if paper.evaluation.weaknesses:
            parts.append("不足: " + "; ".join(paper.evaluation.weaknesses))

        return Document(
            page_content="\n".join(parts),
            metadata={
                "type": "paper",
                "id": paper.id,
                "title": paper.title,
                "year": paper.year,
                "competition": paper.competition,
                "problem_id": paper.problem_id,
                "quality_rating": paper.quality_rating,
            },
        )

    @staticmethod
    def _template_to_document(tpl: Template) -> Document:
        parts = [f"框架名称: {tpl.name}"]
        for step in tpl.steps:
            parts.append(f"\n步骤{step.step}: {step.name}")
            if step.guiding_questions:
                parts.append("引导问题:")
                parts.extend(f"  - {q}" for q in step.guiding_questions)
            if step.decision_tree:
                parts.append("决策路径:")
                parts.extend(f"  - {d}" for d in step.decision_tree)
            if step.checklist:
                parts.append("检查清单:")
                parts.extend(f"  - {c}" for c in step.checklist)

        return Document(
            page_content="\n".join(parts),
            metadata={
                "type": "template",
                "id": tpl.id,
                "name": tpl.name,
                "applicable_to": tpl.applicable_to,
            },
        )

    @staticmethod
    def _problem_to_document(prob: Problem) -> Document:
        parts = [
            f"赛题: {prob.title}",
            f"年份: {prob.year} | 竞赛: {prob.competition} | 题号: {prob.problem_id}",
            f"问题类型: {prob.tags.get('problem_type', [])}",
        ]
        if prob.background:
            parts.append(f"背景: {prob.background}")
        if prob.objectives:
            parts.append("求解目标:")
            parts.extend(f"  - {o}" for o in prob.objectives)
        if prob.data_description:
            parts.append(f"数据描述: {prob.data_description}")
        if prob.deliverables:
            parts.append("提交要求:")
            parts.extend(f"  - {d}" for d in prob.deliverables)
        if prob.full_text:
            parts.append(f"完整题目: {prob.full_text[:1500]}")

        return Document(
            page_content="\n".join(parts),
            metadata={
                "type": "problem",
                "id": prob.id,
                "year": prob.year,
                "competition": prob.competition,
                "problem_id": prob.problem_id,
                "title": prob.title,
                "linked_papers": prob.linked_papers,
            },
        )

    # ── merge & dedup ──────────────────────────────────────────────────

    @staticmethod
    def _merge_results(
        tag_docs: List[Document],
        vector_docs: List[Document],
        k: int,
    ) -> List[Document]:
        """Merge tag and vector results, deduplicating by ID.

        Tag results come first (deterministic, high-confidence matches),
        then vector results fill remaining slots.
        """
        seen_ids: set[str] = set()
        merged: List[Document] = []

        for doc in tag_docs + vector_docs:
            doc_id = doc.metadata.get("id")
            if doc_id and doc_id in seen_ids:
                continue
            if doc_id:
                seen_ids.add(doc_id)
            merged.append(doc)
            if len(merged) >= k:
                break

        return merged

    # ── convenience factory ────────────────────────────────────────────

    def as_langchain_retriever(
        self,
        search_kwargs: Optional[dict] = None,
    ):
        """Return self as a LangChain-compatible retriever (already is one).

        Provided for API parity with vectorstore.as_retriever().
        """
        if search_kwargs:
            # Wrap to inject default kwargs
            original = self._get_relevant_documents

            def with_kwargs(query, *, run_manager=None, **kw):
                merged = {**search_kwargs, **kw}
                return original(query, run_manager=run_manager, **merged)

            self._get_relevant_documents = with_kwargs  # type: ignore[method-assign]

        return self
