"""交互工具集：ask_user（澄清需求）+ run_code（代码执行）。

ask_user:
    LLM 判断用户问题模糊时调用，前端渲染选项卡片让用户选择。
    后端不执行此工具——检测到后直接发 clarify SSE 帧并结束本轮流。

run_code:
    复用 SandboxExecutor 在受限子进程中执行 Python 代码，
    返回 stdout + 生成的图片路径。供 chat/teach 模式使用。
"""

from __future__ import annotations

import json
import logging
from typing import ClassVar, List, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────
# AskUserTool — 向用户提出澄清问题（前端渲染选项卡片）
# ────────────────────────────────────────────────────────────────────


class ClarifyOption(BaseModel):
    label: str = Field(description="选项显示文本（简短）")
    description: str = Field(default="", description="选项补充说明")


class ClarifyQuestion(BaseModel):
    question: str = Field(description="要向用户提出的问题")
    options: List[ClarifyOption] = Field(description="2-4 个选项")
    multiSelect: bool = Field(default=False, description="是否允许多选")


class AskUserInput(BaseModel):
    questions: List[ClarifyQuestion] = Field(
        description="1-3 个需要用户确认的问题",
        min_length=1,
        max_length=3,
    )


class AskUserTool(BaseTool):
    """当用户问题信息不足时，调用此工具向用户提出澄清问题。"""

    name: ClassVar[str] = "ask_user"
    description: ClassVar[str] = (
        "当你无法确定用户的具体需求时调用此工具。"
        "例如：用户只说'帮我建模'但没说是什么类型的问题、有什么数据、目标是什么。"
        "提出 1-3 个关键问题，每个问题给 2-4 个选项供用户选择。"
        "注意：如果用户的问题已经足够明确（如'粒子群算法是什么'），不要调用此工具，直接回答。"
    )
    args_schema: Type[BaseModel] = AskUserInput

    def _run(self, questions: list, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # 此工具不会被后端真正执行——chat_routes 检测到后直接发 clarify 帧
        # 这里只是 fallback（理论上不会走到）
        return json.dumps({"questions": questions}, ensure_ascii=False)


# ────────────────────────────────────────────────────────────────────
# RunCodeTool — 在沙箱中执行 Python 代码
# ────────────────────────────────────────────────────────────────────


class RunCodeInput(BaseModel):
    code: str = Field(
        description=(
            "要执行的 Python 代码。可以使用 numpy, scipy, matplotlib, pandas, sympy 等库。"
            "matplotlib 图表会自动保存为 PNG。"
            "用 print() 输出关键结果。"
        )
    )


class RunCodeTool(BaseTool):
    """在安全沙箱中执行 Python 代码，返回输出结果和生成的图表。"""

    name: ClassVar[str] = "run_code"
    description: ClassVar[str] = (
        "执行 Python 代码进行数值计算、数据分析或绘图。"
        "适用场景：验证公式、数值求解、画函数图/统计图、处理数据。"
        "代码中可用: numpy, scipy, matplotlib, pandas, sympy, cvxpy。"
        "matplotlib 图表会自动保存并返回路径。"
    )
    args_schema: Type[BaseModel] = RunCodeInput

    def _run(self, code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        from ..sandbox.executor import SandboxExecutor

        executor = SandboxExecutor()
        result = executor.run(code)

        parts = []
        if result["stdout"]:
            parts.append(f"输出:\n{result['stdout']}")
        if result["stderr"] and not result["success"]:
            parts.append(f"错误:\n{result['stderr']}")
        if result["images"]:
            parts.append(f"生成图表: {', '.join(result['images'])}")
        if not parts:
            parts.append("代码执行完成，无输出。")

        return "\n".join(parts)


# ────────────────────────────────────────────────────────────────────
# 工厂函数
# ────────────────────────────────────────────────────────────────────


def create_interaction_tools() -> list:
    """创建交互工具列表。"""
    return [AskUserTool(), RunCodeTool()]
