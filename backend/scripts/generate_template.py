"""Generate blank YAML templates for new knowledge base entries.

Usage:
    # Generate a method card template
    python -m scripts.generate_template method --name "粒子群算法" --category optimization

    # Generate a paper template
    python -m scripts.generate_template paper --title "2024国赛A题优秀论文" --year 2024 --competition 国赛

    # Generate a template template
    python -m scripts.generate_template template --name "图论问题分析框架"
"""

import click
from pathlib import Path

KB_ROOT = Path(__file__).parent.parent / "knowledge_base"

# ── templates ──────────────────────────────────────────────────────

METHOD_CARD_TEMPLATE = """method_card:
  id: "{card_id}"
  name: "{name}"
  category: [{category}]

  principle: |
    在此填写方法的核心原理（支持多行，保持缩进一致）。
    说明该方法解决了什么问题，基于什么数学理论。

  formulas:
    - name: "示例公式名"
      latex: "\\\\hat{{I}} = \\\\frac{{V}}{{N}} \\\\sum_{{i=1}}^{{N}} f(x_i)"
      description: "公式含义说明"

  applicable_when:
    - "适用的条件 1"
    - "适用的条件 2"

  not_applicable_when:
    - "不适用的情况 1"
    - "不适用的情况 2"

  typical_scenarios:
    - "典型建模场景 1"
    - "典型建模场景 2"

  common_mistakes:
    - mistake: "常见错误描述"
      solution: "正确做法"

  code_snippets:
    - language: "python"
      description: "代码功能说明"
      code: |
        # 在此填写代码
        import numpy as np
        # ...

  related_cards: [{related_cards}]
  related_papers: [{related_papers}]
"""

PAPER_TEMPLATE = """paper:
  id: "{paper_id}"
  year: {year}
  competition: "{competition}"
  problem_id: "{problem_id}"
  title: "{title}"

  tags:
    problem_type: [{problem_types}]
    core_models: [{core_models}]
    techniques: [{techniques}]

  analysis:
    problem_summary: "一句话概括问题本质"
    key_assumptions:
      - "假设 1"
      - "假设 2"
    decision_variables: "决策变量是什么"
    objective: "目标函数是什么"
    constraints: "主要约束条件"

  model:
    approach: "建模思路概述"
    innovation: "该论文的建模创新点"
    solution_method: "求解算法描述"

  evaluation:
    strengths:
      - "优点 1"
      - "优点 2"
    weaknesses:
      - "不足 1"
      - "不足 2"
    lessons: "可以从这篇论文中学到什么"

  source: "原始来源"
  quality_rating: 3
"""

TEMPLATE_TEMPLATE = """template:
  id: "{tpl_id}"
  name: "{name}"
  applicable_to: [{applicable_to}]

  steps:
    - step: 1
      name: "步骤名称"
      guiding_questions:
        - "引导问题 1"
        - "引导问题 2"
      decision_tree:
        - "如果 A，则 → 方法 X"
        - "如果 B，则 → 方法 Y"
      checklist:
        - "检查项 1"
        - "检查项 2"

    - step: 2
      name: "步骤名称"
      guiding_questions:
        - "引导问题 1"
      checklist:
        - "检查项 1"
"""


# ── ID generators ──────────────────────────────────────────────────

def _next_id(kb_root: Path, prefix: str, subdir: str) -> str:
    """Auto-generate the next sequential ID by scanning existing files."""
    import re

    existing: list[int] = []
    search_dir = kb_root / subdir
    if search_dir.exists():
        for yf in search_dir.rglob("*.yaml"):
            try:
                import yaml

                data = yaml.safe_load(yf.read_text(encoding="utf-8"))
                if data:
                    # Try all top-level keys
                    for key in data:
                        if isinstance(data[key], dict):
                            rid = data[key].get("id", "")
                            m = re.match(rf"^{prefix}(\d+)$", rid)
                            if m:
                                existing.append(int(m.group(1)))
            except Exception:
                continue
    return f"{prefix}{max(existing) + 1:03d}" if existing else f"{prefix}001"


def _next_method_id(kb_root: Path) -> str:
    return _next_id(kb_root, "mc_", "methods")


def _next_paper_id(kb_root: Path) -> str:
    return _next_id(kb_root, "paper_", "papers")


def _next_tpl_id(kb_root: Path) -> str:
    return _next_id(kb_root, "tpl_", "templates")


# ── CLI ────────────────────────────────────────────────────────────


@click.group()
def cli():
    """Generate blank YAML templates for the knowledge base."""


@cli.command()
@click.option("--name", required=True, help="Method name (e.g. 粒子群算法)")
@click.option("--category", default="", help="Category tags, comma-separated (e.g. optimization,启发式)")
@click.option("--subdir", default="", help="Subdirectory under methods/ (e.g. optimization)")
@click.option("--output", default="", help="Custom output path (overrides auto-naming)")
def method(name: str, category: str, subdir: str, output: str):
    """Generate a blank method card YAML."""
    card_id = _next_method_id(KB_ROOT)
    cat_str = ", ".join(f'"{c.strip()}"' for c in category.split(",") if c.strip())

    yaml_content = METHOD_CARD_TEMPLATE.format(
        card_id=card_id,
        name=name,
        category=cat_str or '"在此填写分类"',
        related_cards="",
        related_papers="",
    )

    if output:
        out_path = Path(output)
    else:
        out_dir = KB_ROOT / "methods" / (subdir or "")
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_name = name.replace(" ", "_").replace("/", "_")
        out_path = out_dir / f"{safe_name}.yaml"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml_content, encoding="utf-8")
    click.echo(f"✓ 方法卡片模板已生成: {out_path}")
    click.echo(f"  ID: {card_id}")


@cli.command()
@click.option("--title", required=True, help="Paper title")
@click.option("--year", required=True, type=int, help="Competition year")
@click.option("--competition", default="国赛", help="国赛/美赛/研赛")
@click.option("--problem-id", default="A", help="Problem ID (A/B/C/D/E)")
@click.option("--output", default="", help="Custom output path")
def paper(title: str, year: int, competition: str, problem_id: str, output: str):
    """Generate a blank paper YAML."""
    paper_id = _next_paper_id(KB_ROOT)

    yaml_content = PAPER_TEMPLATE.format(
        paper_id=paper_id,
        year=year,
        competition=competition,
        problem_id=problem_id,
        title=title,
        problem_types="",
        core_models="",
        techniques="",
    )

    if output:
        out_path = Path(output)
    else:
        safe_name = f"{year}{competition}{problem_id}_{title[:15]}".replace(" ", "_")
        out_dir = KB_ROOT / "papers" / competition
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}.yaml"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml_content, encoding="utf-8")
    click.echo(f"✓ 论文模板已生成: {out_path}")
    click.echo(f"  ID: {paper_id}")


@cli.command()
@click.option("--name", required=True, help="Template name (e.g. 图论问题分析框架)")
@click.option("--applicable-to", default="", help="Applicable problem types, comma-separated")
@click.option("--output", default="", help="Custom output path")
def template(name: str, applicable_to: str, output: str):
    """Generate a blank analysis framework template YAML."""
    tpl_id = _next_tpl_id(KB_ROOT)
    app_str = ", ".join(f'"{a.strip()}"' for a in applicable_to.split(",") if a.strip())

    yaml_content = TEMPLATE_TEMPLATE.format(
        tpl_id=tpl_id,
        name=name,
        applicable_to=app_str or '"在此填写适用类型"',
    )

    if output:
        out_path = Path(output)
    else:
        safe_name = name.replace(" ", "_").replace("/", "_")
        out_dir = KB_ROOT / "templates"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{safe_name}.yaml"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml_content, encoding="utf-8")
    click.echo(f"✓ 模板已生成: {out_path}")
    click.echo(f"  ID: {tpl_id}")


if __name__ == "__main__":
    cli()
