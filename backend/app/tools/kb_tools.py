"""LangChain Tools wrapping the knowledge base for agent consumption.

Each tool corresponds to one retrieval path through the three KB layers:
  - search_method_cards   → methods/   (Layer 1: method cards)
  - search_similar_papers → papers/    (Layer 2: past competition papers)
  - get_analysis_framework → templates/ (Layer 3: analysis frameworks)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

from ..knowledge.retriever import HybridRetriever

# ── module-level singleton (lazy-initialised via create_kb_tools) ──────

_retriever: Optional[HybridRetriever] = None
_kb_loader = None  # KnowledgeBaseLoader — set during init


def create_kb_tools(
    kb_root: Path,
    persist_dir: Path,
    embedding_provider: str = "openai",
) -> list:
    """Factory: initialise the shared retriever and return the three KB tools.

    Call once at application startup.  Returns a list of @tool-decorated
    functions ready to be passed to llm.bind_tools(...).
    """
    global _retriever, _kb_loader
    _retriever = HybridRetriever(kb_root, persist_dir, embedding_provider)
    from ..knowledge.loader import KnowledgeBaseLoader

    _kb_loader = KnowledgeBaseLoader(kb_root)
    return [search_method_cards, search_similar_papers,
            get_analysis_framework, search_problems]


# ── helper: format a Document for LLM consumption ─────────────────────


def _format_doc(doc, idx: int = 0) -> str:
    """Render a single Document as a compact, LLM-friendly block."""
    meta = doc.metadata
    type_label = {
        "method_card": "方法卡片",
        "paper": "真题论文",
        "template": "分析框架",
        "problem": "竞赛真题",
    }.get(meta.get("type", ""), "文档")

    score = meta.get("score")
    score_str = f" (相关性: {score:.2f})" if score is not None else ""

    lines = [
        f"[{type_label}] {meta.get('name', meta.get('title', ''))}{score_str}",
        "─" * 56,
    ]

    content = doc.page_content
    # Trim to a reasonable context window per document
    if len(content) > 1200:
        content = content[:1200] + "\n... [已截断]"
    lines.append(content)
    lines.append("─" * 56)
    return "\n".join(lines)


def _format_docs(docs: list) -> str:
    """Render a list of Documents as a single string."""
    if not docs:
        return "（知识库中未找到相关内容）"

    parts = []
    for i, doc in enumerate(docs):
        parts.append(_format_doc(doc, idx=i))
    return "\n\n".join(parts)


# ── Tool 1: search_method_cards ──────────────────────────────────────


@tool
def search_method_cards(query: str, problem_type: str = "") -> str:
    """搜索数学建模方法卡片库。

    输入问题描述或方法关键词，返回最匹配的数学建模方法的原理、适用条件、
    典型应用场景、常见误用和代码示例。

    Args:
        query: 问题描述或方法关键词，如 "资源分配优化"、"时间序列预测"
        problem_type: 可选，问题类型过滤 (optimization/prediction/evaluation/statistics/graph_theory/machine_learning)
    """
    if _retriever is None:
        return "（知识库未初始化，请联系管理员）"

    try:
        docs = _retriever._get_relevant_documents(
            query,
            metadata_filter={"type": "method_card"},
            problem_type=problem_type if problem_type else None,
            k=5,
            use_mmr=True,
            mmr_lambda=0.6,  # slightly favour relevance over diversity for methods
        )
        return _format_docs(docs)
    except Exception as e:
        return f"（检索方法卡片时出错: {e}）"


# ── Tool 2: search_similar_papers ────────────────────────────────────


@tool
def search_similar_papers(query: str, problem_type: str = "") -> str:
    """搜索历年数学建模竞赛真题论文库。

    输入问题描述，返回相似赛题的结构化分析，包括问题概述、建模思路、
    创新点、求解方法和可借鉴之处。

    Args:
        query: 问题描述
        problem_type: 可选，问题类型过滤
    """
    if _retriever is None:
        return "（知识库未初始化，请联系管理员）"

    try:
        docs = _retriever._get_relevant_documents(
            query,
            metadata_filter={"type": "paper"},
            problem_type=problem_type if problem_type else None,
            k=3,
            use_mmr=True,
            mmr_lambda=0.7,  # favour relevance for papers
        )
        return _format_docs(docs)
    except Exception as e:
        return f"（检索论文时出错: {e}）"


# ── Tool 3: get_analysis_framework ───────────────────────────────────


@tool
def get_analysis_framework(problem_type: str) -> str:
    """获取问题分析框架模板。

    根据问题类型返回对应的步骤式分析框架，包含引导性问题、决策树、
    检查清单，指导 Agent 按标准流程分析问题。

    Args:
        problem_type: 问题类型。可选值:
            optimization - 优化问题
            prediction - 预测问题
            evaluation - 评价问题
            statistics - 统计建模
            graph_theory - 图论问题
            differential_equation - 微分方程
    """
    if _retriever is None:
        return "（知识库未初始化，请联系管理员）"

    if not problem_type:
        return "（请指定问题类型 problem_type）"

    try:
        # Template retrieval is purely tag-based (no semantic search needed)
        templates = _retriever._filter_by_tags(problem_type, k=2)
        return _format_docs(templates)
    except Exception as e:
        return f"（获取分析框架时出错: {e}）"


# ── Tool 4: search_problems ──────────────────────────────────────────


@tool
def search_problems(query: str, competition: str = "") -> str:
    """搜索历年数学建模竞赛真题库。

    输入问题描述，返回最匹配的竞赛真题，包括完整题目原文、求解目标、
    数据说明等。可以帮助了解类似问题的完整背景。

    Args:
        query: 问题描述或关键词
        competition: 可选，竞赛过滤 (国赛/美赛/研赛)
    """
    if _retriever is None:
        return "（知识库未初始化，请联系管理员）"

    try:
        metadata_filter = {"type": "problem"}
        docs = _retriever._get_relevant_documents(
            query,
            metadata_filter=metadata_filter,
            k=3,
            use_mmr=True,
            mmr_lambda=0.7,
        )

        # Filter by competition if specified
        if competition and docs:
            docs = [
                d for d in docs
                if d.metadata.get("competition") == competition
            ]

        return _format_docs(docs)
    except Exception as e:
        return f"（检索竞赛真题时出错: {e}）"
