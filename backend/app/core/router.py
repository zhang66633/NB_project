"""动态路由 — 条件边函数（只读状态，返回下一个节点名）。"""

from typing import Literal

from .state import AgentState

AGENT_TO_NODE: dict[str, str] = {
    "analysis": "analysis_agent",
    "modeling": "modeling_agent",
    "solving": "solving_agent",
    "verification": "verification_agent",
    "writing": "writing_agent",
}

NODE_NAMES = Literal[
    "analysis_agent", "modeling_agent", "solving_agent",
    "verification_agent", "writing_agent", "format_response",
]


def route_to_first_agent(state: AgentState) -> NODE_NAMES:
    """plan_execution 后，路由到执行计划中的第一个 agent。"""
    plan: list[str] = state.get("execution_plan", [])
    if not plan:
        return "format_response"
    return AGENT_TO_NODE.get(plan[0], "format_response")


def after_agent_router(state: AgentState) -> NODE_NAMES:
    """每个子 agent 执行完后，决定下一步。

    注意：这是条件边函数，只能返回节点名，不能修改 state。
    current_step_index 由各 agent 节点自行递增。
    """

    # 1. 检查验证失败 → 回退
    if state.get("verification_passed") is False:
        retry = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)

        if retry >= max_retries:
            # 超过最大重试，强制进 writing 或格式化
            plan = state.get("execution_plan", [])
            if "writing" in plan:
                return "writing_agent"
            return "format_response"

        rollback = state.get("rollback_target", "modeling")
        return AGENT_TO_NODE.get(rollback, "format_response")

    # 2. 按计划：current_step_index 已指向当前完成的步骤
    #    下一个是 plan[current_step_index + 1]
    plan: list[str] = state.get("execution_plan", [])
    current_idx: int = state.get("current_step_index", -1)

    next_idx = current_idx + 1
    if next_idx >= len(plan):
        return "format_response"

    return AGENT_TO_NODE.get(plan[next_idx], "format_response")
