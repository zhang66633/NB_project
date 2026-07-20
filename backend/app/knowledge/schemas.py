"""Knowledge base Pydantic schemas for YAML validation."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Formula(BaseModel):
    name: str
    latex: str
    description: str


class CodeSnippet(BaseModel):
    language: str
    description: str
    code: str


class Mistake(BaseModel):
    mistake: str
    solution: str


class MethodCard(BaseModel):
    id: str = Field(pattern=r"^mc_\d+$")
    name: str
    category: List[str]
    principle: str
    formulas: List[Formula] = Field(default_factory=list)
    applicable_when: List[str] = Field(default_factory=list)
    not_applicable_when: List[str] = Field(default_factory=list)
    typical_scenarios: List[str] = Field(default_factory=list)
    common_mistakes: List[Mistake] = Field(default_factory=list)
    code_snippets: List[CodeSnippet] = Field(default_factory=list)
    related_cards: List[str] = Field(default_factory=list)
    related_papers: List[str] = Field(default_factory=list)


class Formula(BaseModel):
    name: str
    latex: str
    description: str


class CodeSnippet(BaseModel):
    language: str
    description: str
    code: str


class Mistake(BaseModel):
    mistake: str
    solution: str


class PaperAnalysis(BaseModel):
    problem_summary: str = ""
    key_assumptions: List[str] = Field(default_factory=list)
    decision_variables: str = ""
    objective: str = ""
    constraints: str = ""


class PaperModel(BaseModel):
    approach: str = ""
    innovation: str = ""
    solution_method: str = ""


class PaperEvaluation(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    lessons: str = ""


class Paper(BaseModel):
    """论文知识卡片 — 深度结构化拆解。

    不仅要记录元数据，更要提取可复用的建模知识：
    方法链、核心公式、算法伪代码、假设分析、常见陷阱。
    """
    id: str = Field(pattern=r"^paper_.+$")
    year: int
    competition: str  # 国赛 / 美赛 / 研赛
    problem_id: str
    title: str
    tags: dict = Field(default_factory=dict)
    # 深度拆解字段（新增）
    problem_context: str = ""           # 问题背景全文（500-1000字）
    methodology_chain: List[str] = Field(default_factory=list)  # 方法链路 ["数据清洗→特征工程→ARIMA预测→线性规划优化"]
    key_formulas: List[Formula] = Field(default_factory=list)   # 论文中出现的核心公式
    algorithm_outline: List[CodeSnippet] = Field(default_factory=list)  # 算法伪代码/步骤
    assumption_analysis: List[str] = Field(default_factory=list)  # 每个假设的合理性分析
    reusable_patterns: List[str] = Field(default_factory=list)   # 可以复用到其他问题的模式
    common_pitfalls: List[Mistake] = Field(default_factory=list) # 效仿本文时易犯的错误
    difficulty_level: str = "medium"    # easy / medium / hard
    # 原有字段
    analysis: PaperAnalysis = Field(default_factory=PaperAnalysis)
    model: PaperModel = Field(default_factory=PaperModel)
    evaluation: PaperEvaluation = Field(default_factory=PaperEvaluation)
    source: str = ""
    quality_rating: int = Field(ge=1, le=5, default=3)


class TemplateStep(BaseModel):
    step: int
    name: str
    guiding_questions: List[str] = Field(default_factory=list)
    decision_tree: List[str] = Field(default_factory=list)
    checklist: List[str] = Field(default_factory=list)


class Template(BaseModel):
    id: str = Field(pattern=r"^tpl_.+$")
    name: str
    applicable_to: List[str] = Field(default_factory=list)
    steps: List[TemplateStep] = Field(default_factory=list)
