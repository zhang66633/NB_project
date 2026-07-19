"""REST API 请求模型。"""

from typing import Literal, Optional
from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    """创建建模任务请求。"""
    problem: str
    mode: Literal["teach", "execute"] = "execute"


class CancelTaskRequest(BaseModel):
    """取消任务请求。"""
    task_id: str


class ApiKeyCreate(BaseModel):
    """添加 API Key 请求。"""
    name: str
    key: str
    provider: str = "anthropic"


class FileUploadRequest(BaseModel):
    """文件上传请求。"""
    filename: Optional[str] = None


# ── Knowledge Base ──────────────────────────────────────────────

class KnowledgeUploadRequest(BaseModel):
    """知识上传 + LLM 提取请求。"""
    text: str
    kb_type: Literal["method", "paper", "template"]
    name: str = ""


class KnowledgeCreateRequest(BaseModel):
    """手动创建知识条目请求。"""
    kb_type: Literal["method", "paper", "template"]
    data: dict  # 根据 type 不同，字段不同


class KnowledgeUpdateRequest(BaseModel):
    """更新知识条目请求。"""
    kb_type: Literal["method", "paper", "template"]
    data: dict
