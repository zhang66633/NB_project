"""REST API 路由 — 连接前端与主编排器。"""

import uuid
import asyncio
import json
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Query
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

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

# ── Auth ─────────────────────────────────────────────────────────

from ..auth import (
    GitHubUser,
    TokenResponse,
    UserResponse,
    get_oauth_client,
    get_current_user,
    require_auth,
    require_contributor,
    create_jwt,
    ALLOWED_CONTRIBUTORS,
)


@api_router.get("/auth/login")
async def github_login():
    """返回 GitHub OAuth 授权 URL。前端跳转到此 URL 开始 GitHub 登录。"""
    settings = get_settings()
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth 未配置。请在 backend/.env 中设置 GITHUB_CLIENT_ID 和 GITHUB_CLIENT_SECRET。"
                   "创建 OAuth App: https://github.com/settings/developers",
        )
    client = get_oauth_client()
    authorize_url = client.get_authorize_url()
    return {"authorize_url": authorize_url}


@api_router.get("/auth/callback")
async def github_callback(code: str = Query(..., description="GitHub OAuth authorization code")):
    """GitHub OAuth 回调 — code 换 token → 拉取 GitHub 用户信息 → 验证身份 → 签发 JWT。

    仅允许项目贡献者（zhang66633、shu639）登录，其他人返回 403。
    """
    client = get_oauth_client()

    # 1. Exchange code for access token
    access_token, exchange_error = await client.exchange_code(code)
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub 授权失败: {exchange_error or '请重试'}",
        )

    # 2. 拉取 GitHub 真实用户信息（确保是本人）
    github_user = await client.get_user(access_token)
    if not github_user:
        raise HTTPException(status_code=400, detail="获取 GitHub 用户信息失败")

    # 3. 安全检查: 只允许项目贡献者登录
    if not client.is_contributor(github_user):
        raise HTTPException(
            status_code=403,
            detail=f"仅限项目贡献者 ({', '.join(sorted(ALLOWED_CONTRIBUTORS))}) 登录。"
                   f"你的 GitHub 账号: {github_user.login}",
        )

    # 4. 签发 JWT
    jwt_token = create_jwt(github_user)

    return TokenResponse(access_token=jwt_token, user=github_user)


@api_router.get("/auth/user", response_model=UserResponse)
async def get_user_info(user: GitHubUser | None = Depends(get_current_user)):
    """获取当前登录用户信息。未登录返回 authenticated=False。"""
    if user is None:
        return UserResponse(authenticated=False)
    is_contributor = user.login.lower() in {c.lower() for c in ALLOWED_CONTRIBUTORS}
    return UserResponse(authenticated=True, user=user, is_contributor=is_contributor)


@api_router.post("/auth/logout")
async def logout():
    """登出（前端清除 JWT 即可）。"""
    return {"success": True, "message": "已登出"}

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

        # 流式运行 — 每个节点完成后立即写入进度消息
        session_mgr = get_session_manager()
        node_names = {
            "classify_problem": "[classify] 识别问题类型...",
            "retrieve_knowledge": "[retrieve] 检索知识库...",
            "plan_execution": "[plan] 制定执行计划...",
            "analysis_agent": "[analysis] 问题分析中...",
            "modeling_agent": "[modeling] 构建数学模型...",
            "solving_agent": "[solving] 编写求解代码...",
            "verification_agent": "[verification] 验证分析中...",
            "writing_agent": "[writing] 生成 LaTeX 论文...",
            "format_response": "[done] 整合输出...",
        }
        messages = []
        final_state = state

        for chunk in orchestrator.stream(state, {"recursion_limit": 50}):
            for node_name, node_output in chunk.items():
                desc = node_names.get(node_name, f"执行: {node_name}")
                progress_msg = {
                    "id": str(uuid.uuid4())[:8],
                    "msg_type": "system",
                    "content": f"[{desc}]",
                    "created_at": None,
                }
                messages.append(progress_msg)
                session_mgr.update(task_id, messages=messages)
                final_state = node_output

        result = final_state

        # 追加 agent 的详细信息到进度消息后面
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
            writing_output=result.get("writing_output", ""),
            analysis_output=result.get("analysis_output", ""),
            model_output=result.get("model_output", ""),
            solving_output=result.get("solving_output", ""),
            verification_output=result.get("verification_output", ""),
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
