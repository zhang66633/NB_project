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


# ── Chat (自由问答) ─────────────────────────────────────────────

class ChatMessage(BaseModel):
    """单条对话消息。"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """自由问答请求。无状态：前端携带完整历史，后端滑动窗口截断。"""
    messages: list[ChatMessage]
    use_rag: bool = False  # 预留：后续挂知识库检索
    # 对话模式：chat=自由问答（直接给结论），teach=教学模式（苏格拉底式引导，不直接给答案）
    mode: Literal["chat", "teach"] = "chat"


class ApiKeyCreate(BaseModel):
    """添加 API Key 请求。"""
    name: str
    key: str
    provider: str = "openai"
    model_name: str = "deepseek-chat"


class ApiKeyQuickCreate(BaseModel):
    """快速添加 API Key — 只需粘贴 key，其他自动识别。"""
    key: str
    name: str = ""


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
