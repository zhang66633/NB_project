"""生成带内嵌 Python 图表的 LaTeX 论文。"""
import os, sys, base64
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# API Key 从 .env 文件读取，请复制 .env.example 为 .env 并填入你的 Key
from dotenv import load_dotenv; load_dotenv(override=True)

from app.core.state import create_initial_state
from app.core.nodes import writing_agent_node
from app.sandbox.executor import SandboxExecutor

# ---- 1. 用 Python 生成图表 ----
print(">>> 用 Python 生成图表...")
chart_code = r"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 数据
x_A = np.linspace(0, 65, 500)
x_B_mat = (120 - 2*x_A) / 3   # 材料约束
x_B_time = (100 - 3*x_A) / 2   # 工时约束
y_upper = np.minimum(np.maximum(x_B_mat, 0), np.maximum(x_B_time, 0))
y_upper = np.where((x_B_mat >= 0) & (x_B_time >= 0), np.minimum(x_B_mat, x_B_time), np.nan)

# 图1: 可行域
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.fill_between(x_A, 0, np.nan_to_num(y_upper, 0), alpha=0.3, color='lightblue')
ax1.plot(x_A, np.maximum(x_B_mat, 0), 'r-', lw=2, label=r'$2x_A+3x_B=120$ (材料)')
ax1.plot(x_A, np.maximum(x_B_time, 0), 'b-', lw=2, label=r'$3x_A+2x_B=100$ (工时)')
ax1.plot(12, 32, 'ro', markersize=10, label=r'最优解 (12,32)')
ax1.axhline(0, color='gray', lw=0.5); ax1.axvline(0, color='gray', lw=0.5)
ax1.set_xlim(0, 60); ax1.set_ylim(0, 55)
ax1.set_xlabel('$x_A$ (A日产量/件)'); ax1.set_ylabel('$x_B$ (B日产量/件)')
ax1.set_title('可行域与最优解'); ax1.legend(loc='upper right'); ax1.grid(alpha=0.3)

# 等利润线
for z in [400, 800, 1200, 1440]:
    xx = np.linspace(0, 40, 100)
    yy = (z - 40*xx) / 30
    mask = yy >= 0
    ax1.plot(xx[mask], yy[mask], 'g--', lw=0.8, alpha=0.5)
ax1.text(20, 23, r'$Z=40x_A+30x_B$', fontsize=9, color='green', rotation=-53)

# 图2: 灵敏度分析
materials = np.linspace(96, 144, 30)
labors = np.linspace(80, 120, 30)
profit_m = []; profit_l = []
for m in materials:
    A = np.array([[2, 3], [3, 2]]); b = np.array([m, 100])
    try:
        sol = np.linalg.solve(A, b)
        if np.all(sol >= 0):
            profit_m.append(40*sol[0] + 30*sol[1])
        else:
            profit_m.append(None)
    except: profit_m.append(None)
for t in labors:
    A = np.array([[2, 3], [3, 2]]); b = np.array([120, t])
    try:
        sol = np.linalg.solve(A, b)
        if np.all(sol >= 0):
            profit_l.append(40*sol[0] + 30*sol[1])
        else:
            profit_l.append(None)
    except: profit_l.append(None)

ax2.plot(materials, profit_m, 'b-o', markersize=4, label='材料变动')
ax2_twin = ax2.twinx()
ax2_twin.plot(labors, profit_l, 'r-s', markersize=4, label='工时变动')
ax2.set_xlabel('资源量'); ax2.set_ylabel('最大利润 (元)')
ax2.set_title('灵敏度分析'); ax2.grid(alpha=0.3)
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1+lines2, labels1+labels2, loc='lower right')

plt.tight_layout()
plt.savefig('charts_combined.png', dpi=150, bbox_inches='tight')
plt.close()
print('图表生成完毕')
"""

sandbox = SandboxExecutor()
exec_result = sandbox.run(chart_code)
if exec_result["success"]:
    images = exec_result.get("images", [])
    if images:
        import shutil
        os.makedirs("images", exist_ok=True)
        shutil.copy(images[0], "images/charts_combined.png")
        print(f"图表已保存: images/charts_combined.png")
else:
    print(f"图表生成失败: {exec_result['stderr'][:500]}")
    sys.exit(1)

# ---- 2. 将图表转 base64 ----
with open("images/charts_combined.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# ---- 3. 生成包含 base64 图表的 LaTeX ----
print(">>> 生成 LaTeX...")
state = create_initial_state(
    problem_raw="某工厂生产A、B两种产品，每件A利润40元，耗材2kg，工时3h；每件B利润30元，耗材3kg，工时2h。每天可用材料120kg，工时100h。求最大利润的生产方案。",
    mode="execute", session_id="latex_test",
)
state["problem_type"] = "optimization"
state["analysis_output"] = """## 问题分析
- 产品A: 利润40元/件, 耗材2kg/件, 工时3h/件
- 产品B: 利润30元/件, 耗材3kg/件, 工时2h/件
- 资源: 材料120kg/天, 工时100h/天
- 决策变量: x_A = A日产量, x_B = B日产量
- 目标: 最大化 Z = 40x_A + 30x_B"""
state["model_output"] = """## 模型建立
目标函数: max Z = 40x_A + 30x_B
约束: 2x_A + 3x_B ≤ 120, 3x_A + 2x_B ≤ 100, x_A,x_B ≥ 0
类型: 线性规划(LP)"""
state["solving_output"] = """## 求解结果
最优解: x_A = 12, x_B = 32
最大利润: Z = 1440元
资源利用: 材料100%, 工时100%
Python代码已生成以上图表"""
state["verification_output"] = """## 验证分析
判定: PASS
手工验算: 2×12+3×32=120, 3×12+2×32=100 ✓
影子价格: 材料2元/kg, 工时12元/h"""

result = writing_agent_node(state)
paper = result.get("writing_output", "")

# ---- 4. 把 base64 图表注入 LaTeX ----
# 找到 \\includegraphics 那一行，替换为 base64 内嵌版本
import re

# 如果没有 includegraphics，在 \\begin{document} 后插入图表宏
if "includegraphics" not in paper:
    img_macro = f"""
% ---- 内嵌图表（Python matplotlib 生成）----
\\usepackage{{graphicx}}

% base64 图片内嵌方案
\\makeatletter
\\newcommand{{\\embedbase64}}[2]{{%
  \\immediate\\openout\\@base64out=#1.base64
  \\immediate\\write\\@base64out{{#2}}
  \\immediate\\closeout\\@base64out
}}
\\makeatother

% 写入临时文件（将 base64 解码为 PNG）
\\newwrite\\tmpout
\\immediate\\openout\\tmpout=temp_img.b64
\\immediate\\write\\tmpout{{{img_b64[:200]}}}
\\immediate\\closeout\\tmpout

% 使用 shell 解码（需 -shell-escape）
% 若无法 shell-escape，图表单独提供为 images/charts_combined.png
\\IfFileExists{{images/charts_combined.png}}{{%
  \\usepackage{{graphicx}}
}}{{}}
"""
    # 简单方案：直接用 filecontents 写入 base64，然后告知用户解码
    paper = paper.replace(
        "\\begin{document}",
        "\\begin{document}\n\n% Python matplotlib 生成的图表（base64编码，见附录）"
    )

# 在末尾添加 Python 图表代码附录
paper = paper.replace(
    "\\end{document}",
    f"""% ============================================
\\section*{{附录：Python 图表生成代码}}
以下代码使用 matplotlib 生成论文中的图表：

\\\\begin{{verbatim}}
{chart_code[:2000]}
\\\\end{{verbatim}}

% 图表 base64 编码（可将以下内容保存为 .b64 文件并用 base64 -d 解码）：
% 长度: {len(img_b64)} 字符
% 解码命令: base64 -d chart.b64 > chart.png

\\end{{document}}"""
)

# 写入文件
with open("output_paper.tex", "w", encoding="utf-8") as f:
    f.write(paper)

print(f"论文已保存到 output_paper.tex ({len(paper)} 字)")
print(f"图表: images/charts_combined.png ({os.path.getsize('images/charts_combined.png')/1024:.1f} KB)")
print()
print("===== LaTeX 前 2000 字 =====")
print(paper[:2000])
