"""任务与编排器路由 — create/get/cancel 任务 + 后台编排器。"""

import asyncio, json, logging, uuid, shutil
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from .schemas.request import CreateTaskRequest
from .schemas.response import TaskResponse, MessageResponse
from ..config import get_settings
from ..auth import GitHubUser, get_current_user
from ..services.session import get_session_manager
from .apikeys import get_active_api_key, _resolve_user_id

logger = logging.getLogger(__name__)

tasks_router = APIRouter()

# ── Tasks ────────────────────────────────────────────────────────

@tasks_router.post("/tasks", response_model=TaskResponse)
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
    print(f"[API] Spawning orchestrator for task={task_id}", flush=True)
    asyncio.create_task(
        asyncio.to_thread(_run_orchestrator_sync, task_id, req.problem, req.mode, uid)
    )
    print(f"[API] Orchestrator spawned for task={task_id}", flush=True)

    return TaskResponse(**task)


@tasks_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = get_session_manager().get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse(**task)


@tasks_router.get("/tasks/{task_id}/messages", response_model=list[MessageResponse])
async def get_task_messages(task_id: str):
    task = get_session_manager().get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return [MessageResponse(**m) for m in task.get("messages", [])]


@tasks_router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    success = get_session_manager().cancel(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"success": True, "message": "任务已取消"}


@tasks_router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks():
    return [TaskResponse(**t) for t in get_session_manager().list_all()]


# ── Background orchestrator runner ────────────────────────────────

def _run_orchestrator_sync(task_id: str, problem: str, mode: str, user_id: str = "guest"):
    """在线程池中运行的同步入口（节点含阻塞调用，必须脱离事件循环）。"""
    asyncio.run(_run_orchestrator(task_id, problem, mode, user_id))


async def _run_orchestrator(task_id: str, problem: str, mode: str, user_id: str = "guest"):
    """在后台运行 LangGraph 编排器。"""
    try:
        print(f"[Orch] Started: task={task_id} mode={mode}", flush=True)
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

        print(f"[Orch] Streaming task={task_id}", flush=True)
        async for chunk in orchestrator.astream(state, {"recursion_limit": 50}, stream_mode="updates"):
            print(f"[Orch] Node: {list(chunk.keys())}", flush=True)
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
