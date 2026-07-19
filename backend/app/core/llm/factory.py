"""LLMFactory — 按 agent 角色创建不同的 LLM 实例。

Uses the provider abstraction layer for clean separation of
API-specific instantiation logic.
"""

import os

from langchain_core.language_models import BaseChatModel

from app.config import get_settings
from .providers import get_provider


class LLMFactory:
    """为每个 agent 角色创建独立配置的 LLM 实例。"""

    @staticmethod
    def create(agent_role: str) -> BaseChatModel:
        settings = get_settings()

        # 获取 agent 对应的模型名
        model_attr = f"{agent_role}_model"
        model = getattr(settings, model_attr, None)

        # 回退: 尝试从环境变量读取统一模型名
        if not model:
            model = os.getenv("DEFAULT_MODEL", "deepseek-chat")

        # 获取 API Key
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or ""

        # If model looks Anthropic, use Anthropic key
        if "claude" in model.lower():
            api_key = os.getenv("ANTHROPIC_API_KEY") or api_key

        # 委托给 provider
        provider = get_provider(model)
        return provider.create(
            model=model,
            api_key=api_key,
            temperature=settings.default_temperature,
            max_tokens=settings.default_max_tokens,
        )


def get_llm(agent_role: str) -> BaseChatModel:
    """快捷获取 LLM 实例。"""
    return LLMFactory.create(agent_role)
