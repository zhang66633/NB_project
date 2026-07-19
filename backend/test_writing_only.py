"""单独测试写作 Agent — 生成 LaTeX 论文。"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ["DEEPSEEK_API_KEY"] = "YOUR_DEEPSEEK_KEY_HERE"
os.environ["OPENAI_API_KEY"] = "YOUR_DEEPSEEK_KEY_HERE"
from dotenv import load_dotenv; load_dotenv(override=True)

from app.core.state import create_initial_state
from app.core.nodes import writing_agent_node

# 构造已有前序输出的状态
state = create_initial_state(
    problem_raw="某工厂生产A、B两种产品，每件A利润40元，耗材2kg，工时3h；每件B利润30元，耗材3kg，工时2h。每天可用材料120kg，工时100h。求最大利润的生产方案。",
    mode="execute",
    session_id="writing_test",
)

# 预填前序 Agent 输出（跳过重复计算）
state["problem_type"] = "optimization"
state["analysis_output"] = """## 问题分析
### 已知条件
- 产品A: 利润40元/件, 耗材2kg/件, 工时3h/件
- 产品B: 利润30元/件, 耗材3kg/件, 工时2h/件
- 资源: 材料120kg/天, 工时100h/天

### 决策变量
x_A = A日产量, x_B = B日产量

### 约束条件
- 材料: 2x_A + 3x_B <= 120
- 工时: 3x_A + 2x_B <= 100
- 非负: x_A >= 0, x_B >= 0"""

state["model_output"] = """## 模型建立
目标函数: max Z = 40x_A + 30x_B
约束:
- 2x_A + 3x_B <= 120
- 3x_A + 2x_B <= 100
- x_A, x_B >= 0
模型类型: 线性规划(LP)"""

state["solving_output"] = """## 求解结果
最优解: x_A = 12, x_B = 32
最大利润: Z = 1440元
资源利用: 材料100%, 工时100%
图表: 可行域图(figure_1.png), 灵敏度图(figure_2.png)"""

state["verification_output"] = """## 验证分析
判定: PASS
- 手工验算通过: 2*12+3*32=120, 3*12+2*32=100
- 影子价格: 材料2元/kg, 工时12元/h
- 工时是最敏感参数"""

print("生成 LaTeX 论文...")
result = writing_agent_node(state)

paper = result.get("writing_output", "")

if paper:
    with open("output_paper.tex", "w", encoding="utf-8") as f:
        f.write(paper)
    print(f"论文已保存到 output_paper.tex ({len(paper)} 字)")
    print()
    print("===== LaTeX 论文（前3000字）=====")
    print(paper[:3000])
else:
    print("生成失败！")
