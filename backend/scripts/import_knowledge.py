"""LLM-powered knowledge extraction — raw text → structured YAML.

Usage:
    # From a text file
    python -m scripts.import_knowledge --input notes.txt --type method --name "粒子群算法"

    # From paste / stdin
    python -m scripts.import_knowledge --type paper --stdin

    # Batch import all files in _import_queue/
    python -m scripts.import_knowledge --batch

    # Preview only (no file written)
    python -m scripts.import_knowledge --input notes.txt --type method --dry-run

The tool uses your configured LLM to extract structured knowledge from
unstructured text and writes a properly formatted YAML file.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

import click

from app.config import get_settings
from app.core.llm.factory import LLMFactory  # type: ignore[import-not-found]

KB_ROOT = Path(__file__).parent.parent / "knowledge_base"
IMPORT_QUEUE = KB_ROOT / "_import_queue"

# ── extraction prompts ─────────────────────────────────────────────

EXTRACT_METHOD_PROMPT = """你是一个数学建模知识工程师。请从以下文本中提取方法卡片的结构化信息。

文本内容:
```
{raw_text}
```

请返回严格的 JSON 格式（不要有任何额外文本），结构如下:
{{
  "name": "方法名称",
  "category": ["分类1", "分类2"],
  "principle": "核心原理的详细描述",
  "formulas": [
    {{"name": "公式名", "latex": "LaTeX表达式", "description": "含义"}}
  ],
  "applicable_when": ["适用条件1", "适用条件2"],
  "not_applicable_when": ["不适用条件1"],
  "typical_scenarios": ["典型场景1", "典型场景2"],
  "common_mistakes": [
    {{"mistake": "常见错误", "solution": "正确做法"}}
  ],
  "code_snippets": [
    {{"language": "python", "description": "功能", "code": "代码内容"}}
  ],
  "related_cards": [],
  "related_papers": []
}}

如果文本中没有某项信息，使用空数组 [] 代替。
如果内容不完整，尽力提取，不要编造不存在的内容。
只返回 JSON，不要有其他解释。"""

EXTRACT_PAPER_PROMPT = """你是一个数学建模竞赛论文分析专家。请从以下文本中提取论文的结构化分析。

文本内容:
```
{raw_text}
```

请返回严格的 JSON 格式:
{{
  "title": "论文标题",
  "year": 年份数字,
  "competition": "国赛/美赛/研赛",
  "problem_id": "题号A/B/C/D/E",
  "tags": {{
    "problem_type": ["优化", "预测"],
    "core_models": ["线性回归", "ARIMA"],
    "techniques": ["数据预处理", "相关性分析"]
  }},
  "analysis": {{
    "problem_summary": "问题本质概述",
    "key_assumptions": ["假设1", "假设2"],
    "decision_variables": "决策变量描述",
    "objective": "目标函数描述",
    "constraints": "约束条件描述"
  }},
  "model": {{
    "approach": "建模思路概述",
    "innovation": "创新点",
    "solution_method": "求解方法"
  }},
  "evaluation": {{
    "strengths": ["优点1"],
    "weaknesses": ["不足1"],
    "lessons": "可学之处"
  }},
  "source": "来源",
  "quality_rating": 3
}}

只返回 JSON，不要有其他解释。"""

EXTRACT_TEMPLATE_PROMPT = """你是一个数学建模教学专家。请从以下文本中提取问题分析框架模板。

文本内容:
```
{raw_text}
```

请返回严格的 JSON 格式:
{{
  "name": "框架名称",
  "applicable_to": ["适用类型1", "适用类型2"],
  "steps": [
    {{
      "step": 1,
      "name": "步骤名称",
      "guiding_questions": ["引导问题1", "引导问题2"],
      "decision_tree": ["若A则X", "若B则Y"],
      "checklist": ["检查项1", "检查项2"]
    }}
  ]
}}

只返回 JSON，不要有其他解释。"""


# ── extraction logic ───────────────────────────────────────────────


def _extract_json(raw_text: str, prompt_template: str, llm) -> dict:
    """Send raw text to LLM, parse structured JSON from response."""
    from langchain_core.messages import HumanMessage

    prompt = prompt_template.format(raw_text=raw_text)
    response = llm.invoke([HumanMessage(content=prompt)])
    text = str(response.content)

    # Strip markdown fences if present
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        # Try to find a JSON object directly
        obj_match = re.search(r"\{.*\}", text, re.DOTALL)
        if obj_match:
            text = obj_match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        click.echo(f"⚠ LLM 返回的不是合法 JSON: {e}", err=True)
        click.echo(f"原始响应:\n{text[:500]}...", err=True)
        return {}


def _next_id(kb_root: Path, prefix: str, subdir: str) -> str:
    """Generate the next sequential ID."""
    existing: list[int] = []
    search_dir = kb_root / subdir
    if search_dir.exists():
        import yaml

        for yf in search_dir.rglob("*.yaml"):
            try:
                data = yaml.safe_load(yf.read_text(encoding="utf-8"))
                if data:
                    for key in data:
                        if isinstance(data[key], dict):
                            rid = data[key].get("id", "")
                            m = re.match(rf"^{prefix}(\d+)$", rid)
                            if m:
                                existing.append(int(m.group(1)))
            except Exception:
                continue
    val = max(existing) + 1 if existing else 1
    if prefix == "paper_":
        return f"{prefix}{val:03d}"
    return f"{prefix}{val:03d}"


def _build_method_yaml(extracted: dict, card_id: str) -> str:
    """Convert extracted JSON to method card YAML string."""
    import yaml

    data = {
        "method_card": {
            "id": card_id,
            "name": extracted.get("name", ""),
            "category": extracted.get("category", []),
            "principle": extracted.get("principle", ""),
            "formulas": extracted.get("formulas", []),
            "applicable_when": extracted.get("applicable_when", []),
            "not_applicable_when": extracted.get("not_applicable_when", []),
            "typical_scenarios": extracted.get("typical_scenarios", []),
            "common_mistakes": extracted.get("common_mistakes", []),
            "code_snippets": extracted.get("code_snippets", []),
            "related_cards": extracted.get("related_cards", []),
            "related_papers": extracted.get("related_papers", []),
        }
    }
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2)


def _build_paper_yaml(extracted: dict, paper_id: str) -> str:
    """Convert extracted JSON to paper YAML string."""
    import yaml

    data = {
        "paper": {
            "id": paper_id,
            "year": extracted.get("year", 2025),
            "competition": extracted.get("competition", ""),
            "problem_id": str(extracted.get("problem_id", "")),
            "title": extracted.get("title", ""),
            "tags": extracted.get("tags", {}),
            "analysis": extracted.get("analysis", {}),
            "model": extracted.get("model", {}),
            "evaluation": extracted.get("evaluation", {}),
            "source": extracted.get("source", ""),
            "quality_rating": extracted.get("quality_rating", 3),
        }
    }
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2)


def _build_template_yaml(extracted: dict, tpl_id: str) -> str:
    """Convert extracted JSON to template YAML string."""
    import yaml

    data = {
        "template": {
            "id": tpl_id,
            "name": extracted.get("name", ""),
            "applicable_to": extracted.get("applicable_to", []),
            "steps": extracted.get("steps", []),
        }
    }
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False, indent=2)


def _import_one(
    raw_text: str,
    kb_type: str,
    name_hint: str,
    llm,
    dry_run: bool,
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """Process one piece of raw text into a YAML file."""
    click.echo(f"正在用 LLM 提取 {kb_type} 结构...")

    if kb_type == "method":
        extracted = _extract_json(raw_text, EXTRACT_METHOD_PROMPT, llm)
        if not extracted:
            return None
        card_id = _next_id(KB_ROOT, "mc_", "methods")
        yaml_str = _build_method_yaml(extracted, card_id)
        if not output_path:
            cat = (
                extracted.get("category", ["other"])[0]
                if extracted.get("category")
                else "other"
            )
            safe_name = (extracted.get("name") or name_hint or "untitled").replace(" ", "_")
            output_path = KB_ROOT / "methods" / cat / f"{safe_name}.yaml"

    elif kb_type == "paper":
        extracted = _extract_json(raw_text, EXTRACT_PAPER_PROMPT, llm)
        if not extracted:
            return None
        paper_id = _next_id(KB_ROOT, "paper_", "papers")
        yaml_str = _build_paper_yaml(extracted, paper_id)
        if not output_path:
            competition = extracted.get("competition", "国赛")
            year = extracted.get("year", 2025)
            pid = extracted.get("problem_id", "A")
            safe_name = f"{year}{competition}{pid}".replace(" ", "_")
            output_path = KB_ROOT / "papers" / competition / f"{safe_name}.yaml"

    elif kb_type == "template":
        extracted = _extract_json(raw_text, EXTRACT_TEMPLATE_PROMPT, llm)
        if not extracted:
            return None
        tpl_id = _next_id(KB_ROOT, "tpl_", "templates")
        yaml_str = _build_template_yaml(extracted, tpl_id)
        if not output_path:
            safe_name = (extracted.get("name") or name_hint or "untitled").replace(" ", "_")
            output_path = KB_ROOT / "templates" / f"{safe_name}.yaml"

    else:
        click.echo(f"未知类型: {kb_type}", err=True)
        return None

    if dry_run:
        click.echo(f"\n--- 预览: {output_path} ---")
        click.echo(yaml_str)
        click.echo("--- 预览结束 ---\n")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(yaml_str, encoding="utf-8")
        click.echo(f"✓ 已保存: {output_path}")

    return output_path


# ── CLI ────────────────────────────────────────────────────────────


@click.command()
@click.option("--input", "input_file", default=None, help="Input text file path")
@click.option("--stdin", "from_stdin", is_flag=True, default=False, help="Read from stdin")
@click.option("--batch", is_flag=True, default=False, help="Process all files in _import_queue/")
@click.option(
    "--type",
    "kb_type",
    required=True,
    type=click.Choice(["method", "paper", "template"]),
    help="Knowledge base entry type",
)
@click.option("--name", default="", help="Name hint (used for output filename)")
@click.option("--output", default="", help="Custom output path")
@click.option("--dry-run", is_flag=True, default=False, help="Preview only, don't write files")
def import_knowledge(
    input_file: Optional[str],
    from_stdin: bool,
    batch: bool,
    kb_type: str,
    name: str,
    output: str,
    dry_run: bool,
):
    """Extract structured knowledge from raw text using LLM.

    Supports three input modes:
      1. --input <file>     : process a single text file
      2. --stdin            : read from standard input
      3. --batch            : process all .txt/.md files in _import_queue/
    """
    # Init LLM
    settings = get_settings()
    config = settings.get_llm_config("analysis")
    factory = LLMFactory()
    llm = factory.create(config)

    output_path = Path(output) if output else None

    if batch:
        queue_dir = Path(IMPORT_QUEUE)
        if not queue_dir.exists() or not list(queue_dir.iterdir()):
            click.echo(f"导入队列为空: {queue_dir}")
            click.echo("请将原始文本文件 (.txt/.md) 放入该目录后重新运行")
            return

        text_files = list(queue_dir.glob("*.txt")) + list(queue_dir.glob("*.md"))
        click.echo(f"批量导入 {len(text_files)} 个文件...\n")

        for i, tf in enumerate(text_files, 1):
            click.echo(f"[{i}/{len(text_files)}] {tf.name}")
            raw = tf.read_text(encoding="utf-8")
            result = _import_one(raw, kb_type, tf.stem, llm, dry_run)
            if result and not dry_run:
                # Move processed file to prevent re-processing
                tf.unlink()
            click.echo()
        return

    # Single file mode
    if input_file:
        raw_text = Path(input_file).read_text(encoding="utf-8")
    elif from_stdin:
        raw_text = sys.stdin.read()
    else:
        click.echo("请指定 --input、--stdin 或 --batch", err=True)
        return

    if not raw_text.strip():
        click.echo("输入文本为空", err=True)
        return

    _import_one(raw_text, kb_type, name, llm, dry_run, output_path)


if __name__ == "__main__":
    import_knowledge()
