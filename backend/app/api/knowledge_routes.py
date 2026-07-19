"""Knowledge base management API — browse, search, reindex, upload, and CRUD."""

import re
import uuid

import yaml
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from ..config import get_settings

knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


# ── response models ────────────────────────────────────────────────────


class KBStats(BaseModel):
    methods_count: int = 0
    papers_count: int = 0
    templates_count: int = 0
    total: int = 0


class MethodCardSummary(BaseModel):
    id: str
    name: str
    category: list[str]
    applicable_when: list[str]
    typical_scenarios: list[str]


class MethodCardDetail(BaseModel):
    id: str
    name: str
    category: list[str]
    principle: str
    formulas: list[dict]
    applicable_when: list[str]
    not_applicable_when: list[str]
    typical_scenarios: list[str]
    common_mistakes: list[dict]
    code_snippets: list[dict]
    related_cards: list[str]
    related_papers: list[str]


class PaperSummary(BaseModel):
    id: str
    year: int
    competition: str
    problem_id: str
    title: str
    tags: dict
    quality_rating: int


class PaperDetail(BaseModel):
    id: str
    year: int
    competition: str
    problem_id: str
    title: str
    tags: dict
    analysis: dict
    model: dict
    evaluation: dict
    source: str
    quality_rating: int


class TemplateSummary(BaseModel):
    id: str
    name: str
    applicable_to: list[str]
    steps_count: int


class TemplateDetail(BaseModel):
    id: str
    name: str
    applicable_to: list[str]
    steps: list[dict]


class SearchResult(BaseModel):
    id: str
    type: str
    name: str = ""
    title: str = ""
    snippet: str
    score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]


class ReindexResponse(BaseModel):
    success: bool
    indexed_count: int
    message: str


# ── CRUD response models ─────────────────────────────────────────────


class KnowledgeCrudResponse(BaseModel):
    success: bool
    entry_id: str = ""
    message: str = ""


class KnowledgeUploadJob(BaseModel):
    job_id: str
    status: str  # "processing" | "completed" | "error"
    result: Optional[dict] = None
    error: Optional[str] = None


# ── in-memory job store (upload extraction) ────────────────────────

_extraction_jobs: dict[str, dict] = {}


# ── helpers ─────────────────────────────────────────────────────────


def _get_loader():
    settings = get_settings()
    from ..knowledge.loader import KnowledgeBaseLoader

    return KnowledgeBaseLoader(settings.kb_root)


def _get_retriever():
    settings = get_settings()
    from ..knowledge.retriever import HybridRetriever

    return HybridRetriever(
        kb_root=settings.kb_root,
        persist_dir=settings.chroma_dir,
    )


def _get_embedder():
    settings = get_settings()
    from ..knowledge.embedder import KBEmbedder

    return KBEmbedder(
        kb_root=settings.kb_root,
        persist_dir=settings.chroma_dir,
    )


def _find_yaml_file(kb_type: str, entry_id: str) -> Optional[Path]:
    """Scan knowledge_base/{subdir}/**/*.yaml for the file with matching id."""
    settings = get_settings()
    subdir_map = {"method": "methods", "paper": "papers", "template": "templates"}
    key_map = {"method": "method_card", "paper": "paper", "template": "template"}
    subdir = subdir_map.get(kb_type, kb_type)
    top_key = key_map.get(kb_type, "")
    search_dir = settings.kb_root / subdir
    if not search_dir.exists():
        return None
    for yf in search_dir.rglob("*.yaml"):
        try:
            data = yaml.safe_load(yf.read_text(encoding="utf-8"))
            if data and top_key in data and isinstance(data[top_key], dict):
                if data[top_key].get("id") == entry_id:
                    return yf
        except Exception:
            continue
    return None


def _next_id(kb_type: str) -> str:
    """Auto-generate the next sequential ID."""
    settings = get_settings()
    subdir_map = {"method": "methods", "paper": "papers", "template": "templates"}
    prefix_map = {"method": "mc_", "paper": "paper_", "template": "tpl_"}
    subdir = subdir_map.get(kb_type, kb_type)
    prefix = prefix_map.get(kb_type, "id_")
    search_dir = settings.kb_root / subdir
    existing: list[int] = []
    if search_dir.exists():
        for yf in search_dir.rglob("*.yaml"):
            try:
                data = yaml.safe_load(yf.read_text(encoding="utf-8"))
                if not data:
                    continue
                key_map = {"method": "method_card", "paper": "paper", "template": "template"}
                top_key = key_map.get(kb_type, "")
                if top_key in data and isinstance(data[top_key], dict):
                    rid = data[top_key].get("id", "")
                    m = re.match(rf"^{re.escape(prefix)}(\d+)$", rid)
                    if m:
                        existing.append(int(m.group(1)))
            except Exception:
                continue
    val = max(existing) + 1 if existing else 1
    return f"{prefix}{val:03d}"


# ── stats ───────────────────────────────────────────────────────────────


@knowledge_router.get("/stats", response_model=KBStats)
async def kb_stats():
    """Get KB statistics: counts per layer."""
    loader = _get_loader()
    methods = len(loader.load_all_methods())
    papers = len(loader.load_all_papers())
    templates = len(loader.load_all_templates())
    return KBStats(
        methods_count=methods,
        papers_count=papers,
        templates_count=templates,
        total=methods + papers + templates,
    )


# ── search ──────────────────────────────────────────────────────────────


@knowledge_router.get("/search", response_model=SearchResponse)
async def kb_search(
    q: str = Query(..., description="Search query string"),
    type: Optional[str] = Query(
        None, description="Filter by doc type: method_card / paper / template"
    ),
    problem_type: Optional[str] = Query(
        None, description="Filter by problem type tag"
    ),
    k: int = Query(5, ge=1, le=20, description="Number of results"),
):
    """Semantic + tag-based hybrid search over the knowledge base."""
    try:
        retriever = _get_retriever()
        metadata_filter = {"type": type} if type else None
        docs = retriever._get_relevant_documents(
            q,
            metadata_filter=metadata_filter,
            problem_type=problem_type,
            k=k,
        )

        results = []
        for doc in docs:
            meta = doc.metadata
            results.append(
                SearchResult(
                    id=meta.get("id", ""),
                    type=meta.get("type", "unknown"),
                    name=meta.get("name", ""),
                    title=meta.get("title", ""),
                    snippet=doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""),
                    score=meta.get("score"),
                )
            )

        return SearchResponse(query=q, total=len(results), results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


# ── methods ─────────────────────────────────────────────────────────────


@knowledge_router.get("/methods", response_model=list[MethodCardSummary])
async def list_methods(
    category: Optional[str] = Query(None, description="Filter by category tag"),
):
    """List all method cards, optionally filtered by category."""
    loader = _get_loader()
    if category:
        cards = loader.get_methods_by_category(category)
    else:
        cards = loader.load_all_methods()
    return [MethodCardSummary(**c.model_dump()) for c in cards]


@knowledge_router.get("/methods/{card_id}", response_model=MethodCardDetail)
async def get_method(card_id: str):
    """Get a single method card by ID."""
    loader = _get_loader()
    card = loader.get_method_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"方法卡片 {card_id} 不存在")
    return MethodCardDetail(**card.model_dump())


# ── papers ──────────────────────────────────────────────────────────────


@knowledge_router.get("/papers", response_model=list[PaperSummary])
async def list_papers(
    problem_type: Optional[str] = Query(None, description="Filter by problem type tag"),
    competition: Optional[str] = Query(None, description="Filter: 国赛/美赛/研赛"),
    year: Optional[int] = Query(None, description="Filter by competition year"),
):
    """List all papers with optional filters."""
    loader = _get_loader()
    papers = loader.load_all_papers()

    if problem_type:
        papers = [p for p in papers if problem_type in p.tags.get("problem_type", [])]
    if competition:
        papers = [p for p in papers if p.competition == competition]
    if year:
        papers = [p for p in papers if p.year == year]

    return [PaperSummary(**p.model_dump()) for p in papers]


@knowledge_router.get("/papers/{paper_id}", response_model=PaperDetail)
async def get_paper(paper_id: str):
    """Get a single paper by ID."""
    loader = _get_loader()
    for paper in loader.load_all_papers():
        if paper.id == paper_id:
            return PaperDetail(**paper.model_dump())
    raise HTTPException(status_code=404, detail=f"论文 {paper_id} 不存在")


# ── templates ───────────────────────────────────────────────────────────


@knowledge_router.get("/templates", response_model=list[TemplateSummary])
async def list_templates(
    problem_type: Optional[str] = Query(None, description="Filter by applicable problem type"),
):
    """List all templates, optionally filtered by problem type."""
    loader = _get_loader()
    if problem_type:
        templates = loader.get_templates_for_type(problem_type)
    else:
        templates = loader.load_all_templates()
    return [
        TemplateSummary(
            id=t.id,
            name=t.name,
            applicable_to=t.applicable_to,
            steps_count=len(t.steps),
        )
        for t in templates
    ]


@knowledge_router.get("/templates/{tpl_id}", response_model=TemplateDetail)
async def get_template(tpl_id: str):
    """Get a single template by ID with full steps."""
    loader = _get_loader()
    tpl = loader.get_template_by_id(tpl_id)
    if not tpl:
        raise HTTPException(status_code=404, detail=f"模板 {tpl_id} 不存在")
    return TemplateDetail(**tpl.model_dump())


# ── reindex (enhanced with incremental) ───────────────────────────


@knowledge_router.post("/reindex", response_model=ReindexResponse)
async def kb_reindex(
    incremental: bool = Query(False, description="Incremental mode: only changed files"),
):
    """Trigger a rebuild of the ChromaDB vector index from YAML files."""
    try:
        settings = get_settings()
        from ..knowledge.embedder import KBEmbedder

        embedder = KBEmbedder(
            kb_root=settings.kb_root,
            persist_dir=settings.chroma_dir,
        )
        count = embedder.build_index(incremental=incremental)
        mode = "增量" if incremental else "全量"
        return ReindexResponse(
            success=True,
            indexed_count=count,
            message=f"{mode}索引完成，共 {count} 篇文档",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建索引失败: {str(e)}")


# ── upload + LLM extraction ──────────────────────────────────────


@knowledge_router.post("/upload")
async def upload_knowledge(
    background_tasks: BackgroundTasks,
    text: str = Form(..., description="原始文本内容"),
    kb_type: str = Form(..., description="method / paper / template"),
    name: str = Form("", description="名称提示"),
):
    """上传原始文本，LLM 自动提取结构化知识，保存 YAML 并增量索引。

    返回 job_id，前端轮询 GET /knowledge/jobs/{job_id} 获取结果。
    """
    if kb_type not in ("method", "paper", "template"):
        raise HTTPException(status_code=400, detail="kb_type 必须为 method / paper / template")

    job_id = str(uuid.uuid4())[:8]
    _extraction_jobs[job_id] = {"status": "processing", "result": None, "error": None}

    background_tasks.add_task(_run_extraction, job_id, text, kb_type, name)
    return KnowledgeUploadJob(job_id=job_id, status="processing")


@knowledge_router.get("/jobs/{job_id}", response_model=KnowledgeUploadJob)
async def get_extraction_job(job_id: str):
    """查询 LLM 提取任务状态。"""
    job = _extraction_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return KnowledgeUploadJob(
        job_id=job_id,
        status=job["status"],
        result=job.get("result"),
        error=job.get("error"),
    )


async def _run_extraction(job_id: str, raw_text: str, kb_type: str, name_hint: str):
    """Background task: LLM extract → validate → write YAML → index."""
    try:
        settings = get_settings()
        from ..core.llm.factory import LLMFactory
        from ..knowledge.schemas import MethodCard, Paper, Template

        # 1. LLM extraction
        config = settings.get_llm_config("analysis")
        factory = LLMFactory()
        llm = factory.create(config)

        prompt_map = {
            "method": _EXTRACT_METHOD_PROMPT,
            "paper": _EXTRACT_PAPER_PROMPT,
            "template": _EXTRACT_TEMPLATE_PROMPT,
        }
        schema_map = {
            "method": MethodCard,
            "paper": Paper,
            "template": Template,
        }

        prompt = prompt_map[kb_type].format(raw_text=raw_text)
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        extracted = _parse_llm_json(str(response.content))

        if not extracted:
            _extraction_jobs[job_id] = {
                "status": "error",
                "result": None,
                "error": "LLM 未能提取出有效内容，请检查输入文本",
            }
            return

        # 2. Generate ID and validate
        entry_id = _next_id(kb_type)
        schema_cls = schema_map[kb_type]
        if kb_type == "method":
            extracted["id"] = entry_id
            try:
                validated = schema_cls(**extracted)
            except Exception as ve:
                _extraction_jobs[job_id] = {
                    "status": "error",
                    "result": None,
                    "error": f"LLM 提取的内容格式有误: {ve}",
                }
                return
        elif kb_type == "paper":
            extracted["id"] = entry_id
            try:
                validated = schema_cls(**extracted)
            except Exception as ve:
                _extraction_jobs[job_id] = {
                    "status": "error",
                    "result": None,
                    "error": f"LLM 提取的内容格式有误: {ve}",
                }
                return
        elif kb_type == "template":
            extracted["id"] = entry_id
            try:
                validated = schema_cls(**extracted)
            except Exception as ve:
                _extraction_jobs[job_id] = {
                    "status": "error",
                    "result": None,
                    "error": f"LLM 提取的内容格式有误: {ve}",
                }
                return
        else:
            validated = extracted

        # 3. Build YAML and write file
        top_key = {"method": "method_card", "paper": "paper", "template": "template"}[kb_type]
        yaml_str = yaml.dump(
            {top_key: validated.model_dump() if hasattr(validated, "model_dump") else extracted},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )

        # Determine output path
        subdir_map = {"method": "methods", "paper": "papers", "template": "templates"}
        subdir = subdir_map[kb_type]
        if kb_type == "method":
            cat = (extracted.get("category") or ["other"])[0]
            safe_name = (extracted.get("name") or name_hint or entry_id).replace(" ", "_")
            out_dir = settings.kb_root / subdir / cat
        elif kb_type == "paper":
            competition = extracted.get("competition", "other")
            year = extracted.get("year", 2025)
            pid = extracted.get("problem_id", "X")
            safe_name = f"{year}{competition}{pid}"
            out_dir = settings.kb_root / subdir / competition
        else:
            safe_name = (extracted.get("name") or name_hint or entry_id).replace(" ", "_")
            out_dir = settings.kb_root / subdir

        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}.yaml"
        out_path.write_text(yaml_str, encoding="utf-8")

        # 4. Incremental index
        embedder = _get_embedder()
        embedder.add_document(out_path)

        _extraction_jobs[job_id] = {
            "status": "completed",
            "result": {
                "entry_id": entry_id,
                "entry_type": kb_type,
                "file_path": str(out_path.relative_to(settings.project_root)),
                "yaml_content": yaml_str,
            },
            "error": None,
        }
    except Exception as e:
        _extraction_jobs[job_id] = {
            "status": "error",
            "result": None,
            "error": str(e),
        }


# ── extraction prompts ──────────────────────────────────────────

_EXTRACT_METHOD_PROMPT = """你是一个数学建模知识工程师。请从以下文本中提取方法卡片的结构化信息。

文本内容:
```
{raw_text}
```

请返回严格的 JSON 格式（不要有任何额外文本），结构如下:
{{
  "name": "方法名称",
  "category": ["分类1", "分类2"],
  "principle": "核心原理的详细描述",
  "formulas": [{{"name": "公式名", "latex": "LaTeX表达式", "description": "含义"}}],
  "applicable_when": ["适用条件1"],
  "not_applicable_when": ["不适用条件1"],
  "typical_scenarios": ["典型场景1"],
  "common_mistakes": [{{"mistake": "常见错误", "solution": "正确做法"}}],
  "code_snippets": [{{"language": "python", "description": "功能", "code": "代码内容"}}],
  "related_cards": [],
  "related_papers": []
}}

如果文本中没有某项信息，使用空数组 [] 代替。只返回 JSON。"""

_EXTRACT_PAPER_PROMPT = """你是一个数学建模竞赛论文分析专家。请从以下文本中提取论文的结构化分析。

文本内容:
```
{raw_text}
```

请返回严格的 JSON 格式:
{{
  "year": 年份数字,
  "competition": "国赛/美赛/研赛",
  "problem_id": "题号A/B/C/D/E",
  "title": "论文标题",
  "tags": {{"problem_type": ["优化"], "core_models": ["线性回归"], "techniques": ["数据分析"]}},
  "analysis": {{"problem_summary": "问题概述", "key_assumptions": ["假设1"], "decision_variables": "决策变量", "objective": "目标", "constraints": "约束"}},
  "model": {{"approach": "建模思路", "innovation": "创新点", "solution_method": "求解方法"}},
  "evaluation": {{"strengths": ["优点1"], "weaknesses": ["不足1"], "lessons": "可学之处"}},
  "source": "来源",
  "quality_rating": 3
}}

只返回 JSON。"""

_EXTRACT_TEMPLATE_PROMPT = """你是一个数学建模教学专家。请从以下文本中提取问题分析框架模板。

文本内容:
```
{raw_text}
```

请返回严格的 JSON 格式:
{{
  "name": "框架名称",
  "applicable_to": ["适用类型1"],
  "steps": [{{"step": 1, "name": "步骤名", "guiding_questions": ["问题1"], "decision_tree": ["若A则X"], "checklist": ["检查项1"]}}]
}}

只返回 JSON。"""


def _parse_llm_json(text: str) -> dict:
    """Extract JSON from LLM response (handles markdown fences)."""
    import json
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        obj_match = re.search(r"\{.*\}", text, re.DOTALL)
        if obj_match:
            text = obj_match.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


# ── CRUD: methods ────────────────────────────────────────────────


@knowledge_router.post("/methods", response_model=KnowledgeCrudResponse)
async def create_method(data: dict):
    """手动创建方法卡片（不经过 LLM）。"""
    try:
        entry_id = _next_id("method")
        data["id"] = entry_id
        from ..knowledge.schemas import MethodCard
        validated = MethodCard(**data)

        yaml_str = yaml.dump(
            {"method_card": validated.model_dump()},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )
        settings = get_settings()
        cat = (data.get("category") or ["other"])[0]
        safe_name = (data.get("name") or entry_id).replace(" ", "_")
        out_dir = settings.kb_root / "methods" / cat
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}.yaml"
        out_path.write_text(yaml_str, encoding="utf-8")

        embedder = _get_embedder()
        embedder.add_document(out_path)

        return KnowledgeCrudResponse(success=True, entry_id=entry_id, message="方法卡片已创建")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建失败: {e}")


@knowledge_router.put("/methods/{card_id}", response_model=KnowledgeCrudResponse)
async def update_method(card_id: str, data: dict):
    """更新方法卡片。"""
    try:
        yf = _find_yaml_file("method", card_id)
        if not yf:
            raise HTTPException(status_code=404, detail=f"方法卡片 {card_id} 不存在")

        data["id"] = card_id
        from ..knowledge.schemas import MethodCard
        validated = MethodCard(**data)

        yaml_str = yaml.dump(
            {"method_card": validated.model_dump()},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )
        yf.write_text(yaml_str, encoding="utf-8")

        embedder = _get_embedder()
        embedder.remove_document(card_id)
        embedder.add_document(yf)

        return KnowledgeCrudResponse(success=True, entry_id=card_id, message="方法卡片已更新")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新失败: {e}")


@knowledge_router.delete("/methods/{card_id}", response_model=KnowledgeCrudResponse)
async def delete_method(card_id: str):
    """删除方法卡片：移除 YAML 文件 + 从 ChromaDB 摘除。"""
    try:
        yf = _find_yaml_file("method", card_id)
        if not yf:
            raise HTTPException(status_code=404, detail=f"方法卡片 {card_id} 不存在")

        embedder = _get_embedder()
        embedder.remove_document(card_id)
        yf.unlink()

        return KnowledgeCrudResponse(success=True, entry_id=card_id, message="方法卡片已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")


# ── CRUD: papers ──────────────────────────────────────────────────


@knowledge_router.post("/papers", response_model=KnowledgeCrudResponse)
async def create_paper(data: dict):
    """手动创建论文条目。"""
    try:
        entry_id = _next_id("paper")
        data["id"] = entry_id
        from ..knowledge.schemas import Paper
        validated = Paper(**data)

        yaml_str = yaml.dump(
            {"paper": validated.model_dump()},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )
        settings = get_settings()
        comp = (data.get("competition") or "other")
        year = data.get("year", 2025)
        pid = data.get("problem_id", "X")
        safe_name = f"{year}{comp}{pid}"
        out_dir = settings.kb_root / "papers" / comp
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}.yaml"
        out_path.write_text(yaml_str, encoding="utf-8")

        embedder = _get_embedder()
        embedder.add_document(out_path)

        return KnowledgeCrudResponse(success=True, entry_id=entry_id, message="论文已创建")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建失败: {e}")


@knowledge_router.put("/papers/{paper_id}", response_model=KnowledgeCrudResponse)
async def update_paper(paper_id: str, data: dict):
    """更新论文条目。"""
    try:
        yf = _find_yaml_file("paper", paper_id)
        if not yf:
            raise HTTPException(status_code=404, detail=f"论文 {paper_id} 不存在")

        data["id"] = paper_id
        from ..knowledge.schemas import Paper
        validated = Paper(**data)

        yaml_str = yaml.dump(
            {"paper": validated.model_dump()},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )
        yf.write_text(yaml_str, encoding="utf-8")

        embedder = _get_embedder()
        embedder.remove_document(paper_id)
        embedder.add_document(yf)

        return KnowledgeCrudResponse(success=True, entry_id=paper_id, message="论文已更新")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新失败: {e}")


@knowledge_router.delete("/papers/{paper_id}", response_model=KnowledgeCrudResponse)
async def delete_paper(paper_id: str):
    """删除论文条目。"""
    try:
        yf = _find_yaml_file("paper", paper_id)
        if not yf:
            raise HTTPException(status_code=404, detail=f"论文 {paper_id} 不存在")

        embedder = _get_embedder()
        embedder.remove_document(paper_id)
        yf.unlink()

        return KnowledgeCrudResponse(success=True, entry_id=paper_id, message="论文已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")


# ── CRUD: templates ───────────────────────────────────────────────


@knowledge_router.post("/templates", response_model=KnowledgeCrudResponse)
async def create_template(data: dict):
    """手动创建分析框架模板。"""
    try:
        entry_id = _next_id("template")
        data["id"] = entry_id
        from ..knowledge.schemas import Template
        validated = Template(**data)

        yaml_str = yaml.dump(
            {"template": validated.model_dump()},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )
        settings = get_settings()
        safe_name = (data.get("name") or entry_id).replace(" ", "_")
        out_dir = settings.kb_root / "templates"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}.yaml"
        out_path.write_text(yaml_str, encoding="utf-8")

        embedder = _get_embedder()
        embedder.add_document(out_path)

        return KnowledgeCrudResponse(success=True, entry_id=entry_id, message="模板已创建")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建失败: {e}")


@knowledge_router.put("/templates/{tpl_id}", response_model=KnowledgeCrudResponse)
async def update_template(tpl_id: str, data: dict):
    """更新模板条目。"""
    try:
        yf = _find_yaml_file("template", tpl_id)
        if not yf:
            raise HTTPException(status_code=404, detail=f"模板 {tpl_id} 不存在")

        data["id"] = tpl_id
        from ..knowledge.schemas import Template
        validated = Template(**data)

        yaml_str = yaml.dump(
            {"template": validated.model_dump()},
            allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2,
        )
        yf.write_text(yaml_str, encoding="utf-8")

        embedder = _get_embedder()
        embedder.remove_document(tpl_id)
        embedder.add_document(yf)

        return KnowledgeCrudResponse(success=True, entry_id=tpl_id, message="模板已更新")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新失败: {e}")


@knowledge_router.delete("/templates/{tpl_id}", response_model=KnowledgeCrudResponse)
async def delete_template(tpl_id: str):
    """删除模板条目。"""
    try:
        yf = _find_yaml_file("template", tpl_id)
        if not yf:
            raise HTTPException(status_code=404, detail=f"模板 {tpl_id} 不存在")

        embedder = _get_embedder()
        embedder.remove_document(tpl_id)
        yf.unlink()

        return KnowledgeCrudResponse(success=True, entry_id=tpl_id, message="模板已删除")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")
