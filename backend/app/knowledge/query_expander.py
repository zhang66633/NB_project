"""Query expansion and HyDE (Hypothetical Document Embeddings) for RAG.

Provides:
  - QueryExpander.expand()  → generates 3 query variants (synonyms, angles, keywords)
  - QueryExpander.hyde()    → generates a hypothetical answer to improve embedding matching

Uses a lightweight LLM call (~100 tokens output) for query rewriting.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

_QUERY_EXPAND_SYSTEM = """你是数学建模检索专家。将用户的查询改写为 3 个不同角度的搜索查询。
每个查询从不同维度描述用户的意图：关键词匹配、方法视角、问题类型视角。

返回严格的 JSON 数组：
["查询1: 关键词精确匹配", "查询2: 方法角度", "查询3: 问题类型角度"]

如果用户查询已经是英文或包含专业术语，保留原文并补充中文变体。"""

_QUERY_EXPAND_USER = "改写以下查询为 3 个搜索变体:\n{query}"

_HYDE_SYSTEM = """你是数学建模竞赛论文作者。根据用户的问题，写一段 200-300 字的假想论文摘要。
描述你会用什么方法、什么模型、什么求解思路来解决这个问题。

就像你正在写一篇竞赛论文的摘要部分：包含问题背景、建模方法、求解过程、预期结论。

注意:
- 不要评价或解释，直接写摘要
- 使用中文
- 控制在 200-300 字"""

_HYDE_USER = "问题: {query}\n\n请写出这篇假想论文的摘要:"


class QueryExpander:
    """LLM-based query expansion and HyDE generation."""

    def __init__(self, llm):
        self._llm = llm

    def expand(self, query: str) -> list[str]:
        """Generate 3 query variants for multi-angle retrieval."""
        try:
            msg = [
                SystemMessage(content=_QUERY_EXPAND_SYSTEM),
                HumanMessage(content=_QUERY_EXPAND_USER.format(query=query)),
            ]
            response = self._llm.invoke(msg)
            import json
            import re

            text = str(response.content)
            # Parse JSON array from response
            match = re.search(r"\[.*?\]", text, re.DOTALL)
            if match:
                variants = json.loads(match.group(0))
                if isinstance(variants, list) and len(variants) > 0:
                    # Return original + variants, capped at 3 variants
                    return [q for q in variants[:3] if isinstance(q, str) and q.strip()]
        except Exception:
            pass

        # Fallback: split the query into keyword chunks
        return [query]

    def hyde(self, query: str) -> str:
        """Generate a hypothetical document to improve embedding retrieval."""
        try:
            msg = [
                SystemMessage(content=_HYDE_SYSTEM),
                HumanMessage(content=_HYDE_USER.format(query=query)),
            ]
            response = self._llm.invoke(msg)
            return str(response.content)
        except Exception:
            return query
