"""Application configuration loaded from environment variables."""

from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    """Configuration for a single LLM instance."""

    provider: Literal["anthropic", "openai"] = "anthropic"
    model: str = "claude-sonnet-4-6"
    api_key: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 8192


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Server ----
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # ---- LLM API Keys ----
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # ---- LLM Models (per agent role) ----
    classifier_model: str = "claude-sonnet-4-6"
    planner_model: str = "claude-sonnet-4-6"
    analysis_model: str = "claude-sonnet-4-6"
    modeling_model: str = "claude-sonnet-4-6"
    solving_model: str = "claude-sonnet-4-6"
    verification_model: str = "claude-sonnet-4-6"
    writing_model: str = "claude-sonnet-4-6"

    # ---- LLM Defaults ----
    default_temperature: float = 0.3
    default_max_tokens: int = 8192

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- ChromaDB ----
    chroma_persist_dir: str = "./data/chroma_db"

    # ---- Knowledge Base ----
    kb_root_dir: str = "./knowledge_base"

    # ---- Sandbox ----
    sandbox_timeout: int = 60
    sandbox_max_memory_mb: int = 512

    # ---- GitHub OAuth ----
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:5173/auth/callback"

    # ---- JWT ----
    jwt_secret: str = "change-me-in-production-use-a-random-secret"

    # ---- Project Root ----
    @property
    def project_root(self) -> Path:
        return Path(__file__).parent.parent

    @property
    def kb_root(self) -> Path:
        return self.project_root / self.kb_root_dir

    @property
    def chroma_dir(self) -> Path:
        return self.project_root / self.chroma_persist_dir

    def get_llm_config(self, agent_role: str) -> LLMConfig:
        """Get LLM configuration for a specific agent role."""
        model_attr = f"{agent_role}_model"
        model = getattr(self, model_attr, self.analysis_model)

        provider: Literal["anthropic", "openai"] = "anthropic"
        api_key = self.anthropic_api_key
        if "gpt" in model.lower() or "o1" in model.lower() or "o3" in model.lower():
            provider = "openai"
            api_key = self.openai_api_key

        return LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=self.default_temperature,
            max_tokens=self.default_max_tokens,
        )


settings = Settings()


def get_settings() -> Settings:
    return settings
