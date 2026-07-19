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
    id: str = Field(pattern=r"^paper_.+$")
    year: int
    competition: str  # 国赛 / 美赛 / 研赛
    problem_id: str
    title: str
    tags: dict = Field(default_factory=dict)
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
