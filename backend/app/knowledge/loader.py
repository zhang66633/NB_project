"""YAML knowledge base loader with Pydantic validation."""

from pathlib import Path
from typing import List

import yaml

from .schemas import MethodCard, Paper, Template


class KnowledgeBaseLoader:
    """Load and validate YAML knowledge base files."""

    def __init__(self, kb_root: Path):
        self.kb_root = Path(kb_root)
        self.methods_dir = self.kb_root / "methods"
        self.papers_dir = self.kb_root / "papers"
        self.templates_dir = self.kb_root / "templates"

    def load_all_methods(self) -> List[MethodCard]:
        """Load all method cards from YAML files."""
        cards = []
        for yaml_file in self.methods_dir.rglob("*.yaml"):
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if data and "method_card" in data:
                cards.append(MethodCard(**data["method_card"]))
        return cards

    def load_all_papers(self) -> List[Paper]:
        """Load all structured papers from YAML files."""
        papers = []
        for yaml_file in self.papers_dir.rglob("*.yaml"):
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if data and "paper" in data:
                papers.append(Paper(**data["paper"]))
        return papers

    def load_all_templates(self) -> List[Template]:
        """Load all analysis templates from YAML files."""
        templates = []
        for yaml_file in self.templates_dir.rglob("*.yaml"):
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if data and "template" in data:
                templates.append(Template(**data["template"]))
        return templates

    def get_method_by_id(self, card_id: str) -> MethodCard | None:
        """Find a specific method card by ID."""
        for card in self.load_all_methods():
            if card.id == card_id:
                return card
        return None

    def get_methods_by_category(self, category: str) -> List[MethodCard]:
        """Filter method cards by category."""
        return [
            card
            for card in self.load_all_methods()
            if category in card.category
        ]

    def get_papers_by_type(self, problem_type: str) -> List[Paper]:
        """Find papers matching a problem type tag."""
        results = []
        for paper in self.load_all_papers():
            tags = paper.tags
            types = tags.get("problem_type", [])
            if problem_type in types:
                results.append(paper)
        return results

    def get_template_by_id(self, tpl_id: str) -> Template | None:
        """Find a specific template by ID."""
        for tpl in self.load_all_templates():
            if tpl.id == tpl_id:
                return tpl
        return None

    def get_templates_for_type(self, problem_type: str) -> List[Template]:
        """Find templates applicable to a problem type."""
        results = []
        for tpl in self.load_all_templates():
            if problem_type in tpl.applicable_to:
                results.append(tpl)
        return results
