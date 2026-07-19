"""代码沙箱 — subprocess 安全执行 Python 代码。"""

import subprocess
import tempfile
import os
import uuid
from pathlib import Path
from typing import Optional

from app.config import get_settings


class SandboxExecutor:
    """在受限子进程中执行 Python 代码。"""

    def __init__(self, timeout: Optional[int] = None):
        settings = get_settings()
        self.timeout = timeout or settings.sandbox_timeout
        self.output_dir = Path(tempfile.gettempdir()) / "mathmodel_outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, code: str) -> dict:
        """执行代码，返回 stdout、stderr、图片路径列表。"""
        run_id = str(uuid.uuid4())[:8]
        output_subdir = self.output_dir / run_id
        output_subdir.mkdir(parents=True, exist_ok=True)

        # 包装代码：自动保存 matplotlib 图表
        wrapped_code = self._wrap_code(code, str(output_subdir))

        try:
            result = subprocess.run(
                ["python", "-c", wrapped_code],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(output_subdir),
                encoding="utf-8",
                errors="replace",
            )

            # 收集生成的图片
            images = sorted(output_subdir.glob("*.png"))

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:5000],
                "stderr": result.stderr[:2000],
                "returncode": result.returncode,
                "images": [str(img) for img in images],
                "run_id": run_id,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"执行超时 ({self.timeout}秒)",
                "returncode": -1,
                "images": [],
                "run_id": run_id,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "images": [],
                "run_id": run_id,
            }

    def _wrap_code(self, code: str, output_dir: str) -> str:
        """包装用户代码，自动捕获 matplotlib 输出。"""
        return f'''
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

os.chdir(r"{output_dir}")

# 用户代码
{code}

# 自动保存所有打开的图表
for i in plt.get_fignums():
    fig = plt.figure(i)
    fig.savefig(os.path.join(r"{output_dir}", f"figure_{{i}}.png"),
                dpi=150, bbox_inches="tight")
plt.close("all")
'''
