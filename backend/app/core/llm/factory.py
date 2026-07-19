"""LLMFactory — 按 agent 角色创建不同的 LLM 实例。"""

import os

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from app.config import get_settings


class LLMFactory:
    """为每个 agent 角色创建独立配置的 LLM 实例。"""

    # DeepSeek 默认配置
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    @staticmethod
    def create(agent_role: str) -> BaseChatModel:
        settings = get_settings()

        # 获取 agent 对应的模型名
        model_attr = f"{agent_role}_model"
        model = getattr(settings, model_attr, "deepseek-chat")

        # 获取 API Key
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or ""

        # 判断是否为 DeepSeek 模型
        if "deepseek" in model.lower():
            base_url = os.getenv("DEEPSEEK_BASE_URL", LLMFactory.DEEPSEEK_BASE_URL)
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=settings.default_temperature,
                max_tokens=settings.default_max_tokens,
            )

        # Anthropic 模型
        if "claude" in model.lower():
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model,
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                temperature=settings.default_temperature,
                max_tokens=settings.default_max_tokens,
            )

        # 其他 OpenAI 兼容模型
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=settings.default_temperature,
            max_tokens=settings.default_max_tokens,
        )


def get_llm(agent_role: str) -> BaseChatModel:
    """快捷获取 LLM 实例。"""
    return LLMFactory.create(agent_role)
