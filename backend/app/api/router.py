"""REST API 路由 — 连接前端与主编排器。"""

import uuid
import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks

from .schemas.request import CreateTaskRequest
from .schemas.response import TaskResponse, MessageResponse, HealthResponse
from .ws import ws_router
from .knowledge_routes import knowledge_router

api_router = APIRouter()
api_router.include_router(ws_router)
api_router.include_router(knowledge_router)

# ---- 内存中存储任务状态（后续换 Redis） ----
_task_store: dict[str, dict] = {}


# ---- 健康检查 ----
@api_router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", service="math-model-agent", version="0.1.0")


# ---- 创建任务 ----
@api_router.post("/tasks", response_model=TaskResponse)
async def create_task(req: CreateTaskRequest, background_tasks: BackgroundTasks):
    """创建建模任务，后台启动编排器。"""
    task_id = str(uuid.uuid4())[:8]

    task = {
        "task_id": task_id,
        "status": "running",
        "problem": req.problem,
        "mode": req.mode,
        "final_response": None,
        "messages": [],
    }
    _task_store[task_id] = task

    # 后台运行编排器
    background_tasks.add_task(_run_orchestrator, task_id, req.problem, req.mode)

    return TaskResponse(**task)


# ---- 获取任务 ----
@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse(**task)


# ---- 获取任务消息 ----
@api_router.get("/tasks/{task_id}/messages", response_model=list[MessageResponse])
async def get_task_messages(task_id: str):
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return [MessageResponse(**m) for m in task.get("messages", [])]


# ---- 取消任务 ----
@api_router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    task["status"] = "cancelled"
    return {"success": True, "message": "任务已取消"}


# ---- 任务列表 ----
@api_router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks():
    return [TaskResponse(**t) for t in _task_store.values()]


# ---- API Keys（简版） ----
@api_router.get("/apikeys")
async def list_api_keys():
    return []


@api_router.post("/apikeys")
async def create_api_key():
    return {"id": "placeholder", "message": "API Key 管理待实现"}


@api_router.delete("/apikeys/{key_id}")
async def delete_api_key(key_id: str):
    return {"success": True}


# ---- 文件相关（简版） ----
@api_router.post("/files/upload")
async def upload_file():
    return {"file_id": "placeholder", "message": "文件上传待实现"}


@api_router.get("/files/{file_id}")
async def download_file(file_id: str):
    raise HTTPException(status_code=404, detail="文件下载待实现")


# ---- 图片服务 ----
from fastapi.responses import FileResponse
import tempfile
from pathlib import Path

@api_router.get("/images/{run_id}/{filename}")
async def get_image(run_id: str, filename: str):
    """获取求解 Agent 生成的图表。"""
    img_dir = Path(tempfile.gettempdir()) / "mathmodel_outputs" / run_id
    img_path = img_dir / filename
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(str(img_path), media_type="image/png")


# ---- 后台任务: 运行编排器 ----
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

        task = _task_store.get(task_id)
        if task:
            task["status"] = "completed"
            task["final_response"] = result.get("final_response", "")
            task["messages"] = messages

    except Exception as e:
        task = _task_store.get(task_id)
        if task:
            task["status"] = "error"
            task["final_response"] = f"错误: {str(e)}"
            task["messages"] = [{
                "id": "error",
                "msg_type": "system",
                "content": f"主智能体运行失败: {str(e)}",
            }]
