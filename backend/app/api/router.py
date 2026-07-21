"""REST API 路由 — 连接前端与主编排器。"""

import uuid
import asyncio
import json
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends, Query, Request
from fastapi.responses import FileResponse

from .schemas.request import CreateTaskRequest, ApiKeyCreate, ApiKeyQuickCreate
from .schemas.response import (
    TaskResponse,
    MessageResponse,
    HealthResponse,
    ApiKeyResponse,
)
from .ws import ws_router
from .knowledge_routes import knowledge_router
from .chat_routes import chat_router
from ..config import get_settings

api_router = APIRouter()
api_router.include_router(ws_router)
api_router.include_router(knowledge_router)
api_router.include_router(chat_router)

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
async def create_task(
    req: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    user: GitHubUser | None = Depends(get_current_user),
):
    """创建建模任务，后台启动编排器。"""
    # 检查是否有可用的 API Key
    uid = _resolve_user_id(user=user)
    active_key = get_active_api_key(uid)
    if not active_key:
        raise HTTPException(
            status_code=400,
            detail="请先在首页配置你的 API Key，"
                   "然后再提交任务。",
        )

    session_mgr = get_session_manager()
    task = session_mgr.create(problem=req.problem, mode=req.mode)
    task_id = task["task_id"]

    # 在独立线程中运行编排器（节点含同步阻塞调用 llm.invoke / subprocess），
    # 以免阻塞事件循环导致 HTTP 响应体无法刷新、WS 进度卡住
    asyncio.create_task(
        asyncio.to_thread(_run_orchestrator_sync, task_id, req.problem, req.mode, uid)
    )

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

_api_keys_store: dict[str, dict] = {}  # user_id → {key_id: {name, key, provider, model_name, masked_key}}
_user_default_keys: dict[str, str] = {}  # user_id → default_key_id
_api_keys_file = None


def _get_api_keys_path() -> Path:
    global _api_keys_file
    if _api_keys_file is None:
        settings = get_settings()
        _api_keys_file = settings.project_root / "data" / "apikeys.json"
    return _api_keys_file


def _load_api_keys():
    global _api_keys_store, _user_default_keys
    path = _get_api_keys_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            _api_keys_store = data.get("keys", {})
            _user_default_keys = data.get("default_keys", {})
            # 兼容旧格式: 如果 keys 是 key_id→{...}，转换为 user_id→{key_id→{...}}
            if _api_keys_store and not any(isinstance(v, dict) and any(
                isinstance(vv, dict) and "key" in vv for vv in v.values()
            ) for v in _api_keys_store.values() if isinstance(v, dict)):
                # 旧格式: {key_id: {...}} → 新格式: {"legacy": {key_id: {...}}}
                _api_keys_store = {"legacy": _api_keys_store}
                if _user_default_keys and not isinstance(list(_user_default_keys.values())[0] if _user_default_keys else None, str):
                    _user_default_keys = {"legacy": list(_user_default_keys.values())[0] if isinstance(list(_user_default_keys.values())[0], str) else next(iter(_api_keys_store.get("legacy", {}).keys()), None)}
        except Exception:
            _api_keys_store = {}
            _user_default_keys = {}


def _save_api_keys():
    path = _get_api_keys_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "keys": _api_keys_store,
        "default_keys": _user_default_keys,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_user_id(request: Request | None = None, user: GitHubUser | None = None) -> str:
    """Resolve a user ID for API key scoping.

    - Logged-in GitHub user → use login name
    - Guest → use "guest" (shared guest pool)
    """
    if user and user.login:
        return user.login
    return "guest"


def get_active_api_key(user_id: str | None = None) -> dict | None:
    """获取指定用户的活跃 API Key（优先默认 key，否则返回第一个）。"""
    _load_api_keys()
    uid = user_id or "guest"
    user_keys = _api_keys_store.get(uid, {})
    if not user_keys:
        return None
    default_id = _user_default_keys.get(uid)
    if default_id and default_id in user_keys:
        return user_keys[default_id]
    # 返回用户的第一个 key
    return next(iter(user_keys.values()))


@api_router.get("/apikeys/mine")
async def get_my_api_key(user: GitHubUser | None = Depends(get_current_user)):
    """获取当前用户的 API Key 状态（首页快速检查用）。"""
    _load_api_keys()
    uid = _resolve_user_id(user=user)
    user_keys = _api_keys_store.get(uid, {})
    if not user_keys:
        return {"has_key": False, "key": None}
    # 返回默认 key 或第一个
    active = get_active_api_key(uid)
    return {
        "has_key": True,
        "key": {
            "masked_key": active.get("masked_key", "****") if active else "****",
            "provider": active.get("provider", "") if active else "",
            "model_name": active.get("model_name", "") if active else "",
        } if active else None,
    }


async def _verify_api_key(key: str, provider: str, model_name: str) -> tuple[bool, str]:
    """验证 API Key 是否有效 — 发送一个最小请求测试连通性。"""
    import httpx

    # 确定 base_url
    if "deepseek" in model_name.lower():
        base_url = "https://api.deepseek.com/v1/chat/completions"
    elif provider == "anthropic":
        base_url = "https://api.anthropic.com/v1/messages"
    else:
        base_url = "https://api.openai.com/v1/chat/completions"

    test_model = model_name if "deepseek" in model_name.lower() else (
        "claude-3-haiku-20240307" if provider == "anthropic" else "gpt-3.5-turbo"
    )

    headers = {"Content-Type": "application/json"}
    if provider == "anthropic":
        headers["x-api-key"] = key
        headers["anthropic-version"] = "2023-06-01"
        body = {
            "model": test_model,
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}],
        }
    else:
        headers["Authorization"] = f"Bearer {key}"
        body = {
            "model": test_model,
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}],
        }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(base_url, json=body, headers=headers)
            if resp.status_code == 200:
                return True, ""
            elif resp.status_code == 401 or resp.status_code == 403:
                return False, "API Key 无效或被拒绝，请检查 Key 是否正确"
            elif resp.status_code == 429:
                return False, "API 请求过于频繁，请稍后再试"
            else:
                body_text = resp.text[:200]
                return False, f"API 验证失败 (HTTP {resp.status_code}): {body_text}"
    except httpx.ConnectError:
        return False, "无法连接到 API 服务器，请检查网络"
    except Exception as e:
        return False, f"验证请求失败: {str(e)[:100]}"


@api_router.post("/apikeys/quick")
async def quick_add_api_key(
    req: ApiKeyQuickCreate,
    user: GitHubUser | None = Depends(get_current_user),
):
    """快速添加 API Key — 粘贴 Key，自动识别 + 验证有效性。"""
    _load_api_keys()
    uid = _resolve_user_id(user=user)

    # 自动识别 provider
    key = req.key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="请输入 API Key")

    if key.startswith("sk-ant"):
        provider = "anthropic"
    else:
        provider = "openai"

    # 自动推断模型名
    if provider == "anthropic":
        model_name = "claude-sonnet-4-6"
    else:
        model_name = "deepseek-chat"

    # 验证 Key 是否有效
    valid, err_msg = await _verify_api_key(key, provider, model_name)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Key 验证失败: {err_msg}")

    key_id = str(uuid.uuid4())[:8]
    masked = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"

    if uid not in _api_keys_store:
        _api_keys_store[uid] = {}

    _api_keys_store[uid][key_id] = {
        "name": req.name or f"我的 Key ({masked})",
        "key": key,
        "provider": provider,
        "model_name": model_name,
        "masked_key": masked,
    }

    # 自动设为该用户的默认
    _user_default_keys[uid] = key_id

    _save_api_keys()

    return {
        "success": True,
        "id": key_id,
        "masked_key": masked,
        "provider": provider,
        "model_name": model_name,
        "message": "API Key 验证通过，已激活！Agent 将使用此 Key 进行对话。",
    }


@api_router.get("/apikeys", response_model=list[ApiKeyResponse])
async def list_api_keys(user: GitHubUser | None = Depends(get_current_user)):
    _load_api_keys()
    uid = _resolve_user_id(user=user)
    user_keys = _api_keys_store.get(uid, {})
    default_id = _user_default_keys.get(uid)
    return [
        ApiKeyResponse(
            id=kid,
            name=v.get("name", ""),
            provider=v.get("provider", "openai"),
            model_name=v.get("model_name", "deepseek-chat"),
            masked_key=v.get("masked_key", "****"),
            is_default=kid == default_id,
        )
        for kid, v in user_keys.items()
    ]


@api_router.post("/apikeys", response_model=ApiKeyResponse)
async def create_api_key(req: ApiKeyCreate, user: GitHubUser | None = Depends(get_current_user)):
    _load_api_keys()
    uid = _resolve_user_id(user=user)

    # 验证 Key 是否有效
    valid, err_msg = await _verify_api_key(req.key, req.provider, req.model_name)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Key 验证失败: {err_msg}")

    key_id = str(uuid.uuid4())[:8]
    masked = req.key[:4] + "****" + req.key[-4:] if len(req.key) > 8 else "****"

    if uid not in _api_keys_store:
        _api_keys_store[uid] = {}

    _api_keys_store[uid][key_id] = {
        "name": req.name,
        "key": req.key,
        "provider": req.provider,
        "model_name": req.model_name,
        "masked_key": masked,
    }

    if not _user_default_keys.get(uid):
        _user_default_keys[uid] = key_id

    _save_api_keys()

    return ApiKeyResponse(
        id=key_id,
        name=req.name,
        provider=req.provider,
        model_name=req.model_name,
        masked_key=masked,
        is_default=key_id == _user_default_keys.get(uid),
    )


@api_router.delete("/apikeys/{key_id}")
async def delete_api_key(key_id: str, user: GitHubUser | None = Depends(get_current_user)):
    _load_api_keys()
    uid = _resolve_user_id(user=user)
    user_keys = _api_keys_store.get(uid, {})
    if key_id not in user_keys:
        raise HTTPException(status_code=404, detail="API Key 不存在")
    del _api_keys_store[uid][key_id]
    if _user_default_keys.get(uid) == key_id:
        _user_default_keys[uid] = next(iter(_api_keys_store[uid].keys()), None) if _api_keys_store[uid] else None
    _save_api_keys()
    return {"success": True, "message": "API Key 已删除"}


@api_router.post("/apikeys/{key_id}/default")
async def set_default_api_key(key_id: str, user: GitHubUser | None = Depends(get_current_user)):
    _load_api_keys()
    uid = _resolve_user_id(user=user)
    user_keys = _api_keys_store.get(uid, {})
    if key_id not in user_keys:
        raise HTTPException(status_code=404, detail="API Key 不存在")
    _user_default_keys[uid] = key_id
    _save_api_keys()
    return {"success": True, "message": "已设为默认"}


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

def _run_orchestrator_sync(task_id: str, problem: str, mode: str, user_id: str = "guest"):
    """在线程池中运行的同步入口（节点含阻塞调用，必须脱离事件循环）。"""
    asyncio.run(_run_orchestrator(task_id, problem, mode, user_id))


async def _run_orchestrator(task_id: str, problem: str, mode: str, user_id: str = "guest"):
    """在后台运行 LangGraph 编排器。"""
    try:
        from app.core.state import create_initial_state
        from app.core.workflow import get_orchestrator

        # 获取该用户的活跃 API Key
        active_key = get_active_api_key(user_id)

        orchestrator = get_orchestrator()
        state = create_initial_state(
            problem_raw=problem, mode=mode, session_id=task_id,
            api_key_config=active_key,
        )

        # 流式运行 — 每个节点完成后立即写入进度消息
        session_mgr = get_session_manager()
        publisher = None
        try:
            from app.services.redis_pubsub import get_publisher
            publisher = get_publisher()
        except Exception:
            publisher = None

        node_meta = {
            "classify_problem": ("问题分析", "识别问题类型"),
            "retrieve_knowledge": ("知识检索", "检索建模知识库"),
            "plan_execution": ("计划制定", "规划执行步骤"),
            "analysis_agent": ("问题分析", "深入剖析题意"),
            "modeling_agent": ("模型构建", "建立数学模型"),
            "solving_agent": ("求解计算", "编写并执行求解代码"),
            "verification_agent": ("验证分析", "检验模型鲁棒性"),
            "writing_agent": ("论文写作", "生成 LaTeX 论文"),
            "format_response": ("整合输出", "汇总最终结果"),
        }
        messages = []
        final_state = state

        for chunk in orchestrator.stream(state, {"recursion_limit": 50}):
            for node_name, node_output in chunk.items():
                stage, desc = node_meta.get(node_name, (node_name, f"执行: {node_name}"))
                progress_msg = {
                    "id": str(uuid.uuid4())[:8],
                    "msg_type": "system",
                    "content": f"[{stage}] {desc}...",
                    "created_at": None,
                }
                messages.append(progress_msg)
                session_mgr.update(task_id, messages=messages)
                # 实时推送到 WebSocket（fakeredis 或真实 Redis）
                if publisher:
                    publisher.node_end(
                        task_id,
                        node_name,
                        {"stage": stage, "title": stage, "desc": desc, "status": "completed"},
                    )
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
        # 通知前端任务结束（携带最终答案用于聊天面板展示）
        if publisher:
            publisher.task_end(
                task_id,
                "format_response",
                "completed",
                {"final_response": result.get("final_response", "")[:4000]},
            )

    except Exception as e:
        import traceback
        logger.error("Orchestrator failed for task %s:\n%s", task_id, traceback.format_exc())
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
        try:
            from app.services.redis_pubsub import get_publisher
            get_publisher().task_end(task_id, "orchestrator", "error", {"message": str(e)})
        except Exception:
            pass
    finally:
        # 清理取消事件
        get_session_manager().cleanup_cancel_event(task_id)
