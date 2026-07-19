"""REST API 路由 — 连接前端与主编排器。"""

import uuid
import asyncio
import json
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse

from .schemas.request import CreateTaskRequest, ApiKeyCreate
from .schemas.response import (
    TaskResponse,
    MessageResponse,
    HealthResponse,
    ApiKeyResponse,
)
from .ws import ws_router
from .knowledge_routes import knowledge_router
from ..config import get_settings

api_router = APIRouter()
api_router.include_router(ws_router)
api_router.include_router(knowledge_router)

# ── Session manager ──────────────────────────────────────────────

from ..services.session import get_session_manager

# ── Health check ─────────────────────────────────────────────────

@api_router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", service="math-model-agent", version="0.1.0")


# ── Tasks ────────────────────────────────────────────────────────

@api_router.post("/tasks", response_model=TaskResponse)
async def create_task(req: CreateTaskRequest, background_tasks: BackgroundTasks):
    """创建建模任务，后台启动编排器。"""
    session_mgr = get_session_manager()
    task = session_mgr.create(problem=req.problem, mode=req.mode)
    task_id = task["task_id"]

    # 后台运行编排器
    background_tasks.add_task(_run_orchestrator, task_id, req.problem, req.mode)

    return TaskResponse(**task)


@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = get_session_manager().get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse(**task)


@api_router.get("/tasks/{task_id}/messages", response_model=list[MessageResponse])
async def get_task_messages(task_id: str):
    task = get_session_manager().get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return [MessageResponse(**m) for m in task.get("messages", [])]


@api_router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    success = get_session_manager().cancel(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"success": True, "message": "任务已取消"}


@api_router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks():
    return [TaskResponse(**t) for t in get_session_manager().list_all()]


# ── API Keys ─────────────────────────────────────────────────────

_api_keys_store: dict[str, dict] = {}  # key_id → {name, key, provider, masked_key}

_api_keys_file = None


def _get_api_keys_path() -> Path:
    global _api_keys_file
    if _api_keys_file is None:
        settings = get_settings()
        _api_keys_file = settings.project_root / "data" / "apikeys.json"
    return _api_keys_file


def _load_api_keys():
    global _api_keys_store
    path = _get_api_keys_path()
    if path.exists():
        try:
            _api_keys_store = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            _api_keys_store = {}


def _save_api_keys():
    path = _get_api_keys_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_api_keys_store, ensure_ascii=False, indent=2), encoding="utf-8")


@api_router.get("/apikeys", response_model=list[ApiKeyResponse])
async def list_api_keys():
    _load_api_keys()
    return [
        ApiKeyResponse(
            id=kid,
            name=v.get("name", ""),
            provider=v.get("provider", "anthropic"),
            masked_key=v.get("masked_key", "****"),
        )
        for kid, v in _api_keys_store.items()
    ]


@api_router.post("/apikeys", response_model=ApiKeyResponse)
async def create_api_key(req: ApiKeyCreate):
    _load_api_keys()
    key_id = str(uuid.uuid4())[:8]
    masked = req.key[:4] + "****" + req.key[-4:] if len(req.key) > 8 else "****"

    _api_keys_store[key_id] = {
        "name": req.name,
        "key": req.key,
        "provider": req.provider,
        "masked_key": masked,
    }
    _save_api_keys()

    return ApiKeyResponse(id=key_id, name=req.name, provider=req.provider, masked_key=masked)


@api_router.delete("/apikeys/{key_id}")
async def delete_api_key(key_id: str):
    _load_api_keys()
    if key_id not in _api_keys_store:
        raise HTTPException(status_code=404, detail="API Key 不存在")
    del _api_keys_store[key_id]
    _save_api_keys()
    return {"success": True, "message": "API Key 已删除"}


# ── File upload / download ───────────────────────────────────────

def _get_uploads_dir() -> Path:
    settings = get_settings()
    uploads = settings.project_root / "data" / "uploads"
    uploads.mkdir(parents=True, exist_ok=True)
    return uploads


@api_router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件到 data/uploads/ 目录。"""
    uploads_dir = _get_uploads_dir()
    file_id = str(uuid.uuid4())[:8]
    # Keep original extension
    suffix = Path(file.filename or "upload").suffix
    stored_name = f"{file_id}{suffix}"
    stored_path = uploads_dir / stored_name

    try:
        with stored_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {e}")

    return {
        "file_id": file_id,
        "filename": file.filename,
        "stored_name": stored_name,
        "size": stored_path.stat().st_size,
        "url": f"/api/files/{file_id}",
    }


@api_router.get("/files/{file_id}")
async def download_file(file_id: str):
    """下载已上传的文件。"""
    uploads_dir = _get_uploads_dir()
    # Find the file with this id regardless of extension
    matches = list(uploads_dir.glob(f"{file_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="文件不存在")
    stored_path = matches[0]
    return FileResponse(str(stored_path), media_type="application/octet-stream", filename=stored_path.name)


# ── Image serving ─────────────────────────────────────────────────

import tempfile


@api_router.get("/images/{run_id}/{filename}")
async def get_image(run_id: str, filename: str):
    """获取求解 Agent 生成的图表。"""
    img_dir = Path(tempfile.gettempdir()) / "mathmodel_outputs" / run_id
    img_path = img_dir / filename
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(str(img_path), media_type="image/png")


# ── Background orchestrator runner ────────────────────────────────

async def _run_orchestrator(task_id: str, problem: str, mode: str):
    """在后台运行 LangGraph 编排器。"""
    try:
        from app.core.state import create_initial_state
        from app.core.workflow import get_orchestrator

        orchestrator = get_orchestrator()
        state = create_initial_state(problem_raw=problem, mode=mode, session_id=task_id)

        # 运行编排图（同步方式，在线程池中执行）
        result = await asyncio.to_thread(orchestrator.invoke, state)

        # 收集消息
        messages = []
        for msg in result.get("messages", []):
            messages.append({
                "id": str(uuid.uuid4())[:8],
                "msg_type": msg.__class__.__name__.replace("Message", "").lower(),
                "content": str(msg.content)[:500] if msg.content else None,
                "created_at": None,
            })

        session_mgr = get_session_manager()
        session_mgr.update(
            task_id,
            status="completed",
            final_response=result.get("final_response", ""),
            messages=messages,
        )

    except Exception as e:
        session_mgr = get_session_manager()
        session_mgr.update(
            task_id,
            status="error",
            final_response=f"错误: {str(e)}",
            messages=[{
                "id": "error",
                "msg_type": "system",
                "content": f"主智能体运行失败: {str(e)}",
            }],
        )
    finally:
        # 清理取消事件
        get_session_manager().cleanup_cancel_event(task_id)
