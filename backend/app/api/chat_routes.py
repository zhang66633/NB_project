"""自由问答（纯对话）SSE 流式接口。

不走 LangGraph 建模流水线，不挂 RAG（预留开关），
直接调用 chat 角色 LLM 逐 token 推送，保证响应快。

协议（text/event-stream）：
  - 每个增量:  data: {"delta": "..."}\n\n
  - 完成:      data: [DONE]\n\n
  - 错误:      data: {"error": "..."}\n\n 然后结束
"""

import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .schemas.request import ChatRequest
from ..core.llm.factory import LLMFactory
from ..core.prompts._shared import MARKDOWN_RULES, TEACH_SHARED_RULES
from ..auth import GitHubUser, get_current_user

logger = logging.getLogger(__name__)

chat_router = APIRouter()

# 滑动窗口：保留最近 N 条消息（不含 system），防止多轮后 token 膨胀。
# 后续可在此之上做「窗口外历史 LLM 摘要压缩」，接口不变。
MAX_HISTORY_MESSAGES = 20

CHAT_SYSTEM_PROMPT = f"""# 数学建模助手

你是一位专业、友善的数学建模助手，擅长解答数学建模、算法、优化、统计、
数据分析、竞赛备赛等相关问题，也能进行一般性的技术问答与咨询。

## 回答风格
- 直接、清晰、有条理，先给结论再给解释
- 对概念性问题给出准确定义与直觉解释
- 对方法类问题给出适用场景、步骤与优缺点
- 涉及代码时给出简洁可运行的示例

{MARKDOWN_RULES}"""

TEACH_SYSTEM_PROMPT = f"""# 数学建模引导式导师

你是一位耐心、善于启发的数学建模导师。你的目标不是直接给出答案，
而是通过苏格拉底式提问，引导学生自己一步步建立建模思维。

{TEACH_SHARED_RULES}

## 引导路径（按学生进度灵活调整）
1. 理解题意：核心目标是什么？是优化/预测/评价/统计？
2. 决策变量：哪些量是可以由我们决定的？
3. 约束条件：现实中受到哪些限制？
4. 目标函数：如何用数学表达式描述目标？
5. 模型与方法：哪类模型适合？为什么？

{MARKDOWN_RULES}"""


def _system_prompt(mode: str) -> str:
    return TEACH_SYSTEM_PROMPT if mode == "teach" else CHAT_SYSTEM_PROMPT


def _to_lc_messages(req: ChatRequest) -> list:
    """把请求中的消息历史转成 LangChain 消息，并做滑动窗口截断。"""
    history = req.messages[-MAX_HISTORY_MESSAGES:]
    msgs = [SystemMessage(content=_system_prompt(req.mode))]
    for m in history:
        if m.role == "user":
            msgs.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            msgs.append(AIMessage(content=m.content))
        elif m.role == "system":
            msgs.append(SystemMessage(content=m.content))
    return msgs


async def _event_stream(req: ChatRequest, api_key_config: dict | None = None):
    """SSE 生成器：流式输出 LLM 增量。"""
    try:
        llm = LLMFactory.create("chat", api_key_config=api_key_config)
        messages = _to_lc_messages(req)

        # 预留 RAG：当前直通。后续在此检索 kb_search 并把结果注入 system context。
        if req.use_rag:
            logger.info("use_rag=True 暂未实现，按纯对话处理")

        async for chunk in llm.astream(messages):
            delta = chunk.content
            if not delta:
                continue
            if isinstance(delta, list):  # 某些 provider 返回分段
                delta = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in delta
                )
            if delta:
                yield f"data: {json.dumps({'delta': delta}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:  # noqa: BLE001
        logger.exception("chat stream failed")
        err = str(e)
        # 给出更友好的错误提示
        if "incorrect api key" in err.lower() or "invalid api key" in err.lower():
            err = "API Key 无效，请在首页重新配置你的 Key"
        elif "401" in err or "403" in err:
            err = f"API Key 验证失败 (401)，请检查 Key 是否正确。原始错误: {err[:200]}"
        elif "api_key" in err.lower() or "api key" in err.lower():
            err = f"API Key 错误: {err[:300]}"
        yield f"data: {json.dumps({'error': err}, ensure_ascii=False)}\n\n"


@chat_router.post("/chat")
async def chat(req: ChatRequest, user: GitHubUser | None = Depends(get_current_user)):
    """自由问答 SSE 流式接口。"""
    # 检查是否有可用的 API Key
    from .apikeys import get_active_api_key, _resolve_user_id
    uid = _resolve_user_id(user=user)
    active_key = get_active_api_key(uid)
    if not active_key:
        async def no_key():
            yield f"data: {json.dumps({'error': '请先在首页配置你的 API Key 后再发送消息。'}, ensure_ascii=False)}\n\n"
        return StreamingResponse(no_key(), media_type="text/event-stream")

    if not req.messages:
        async def empty():
            yield f"data: {json.dumps({'error': '消息不能为空'}, ensure_ascii=False)}\n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")

    return StreamingResponse(
        _event_stream(req, api_key_config=active_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 关闭 nginx 缓冲，保证实时性
        },
    )
