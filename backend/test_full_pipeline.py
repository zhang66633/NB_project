"""端到端测试 — 全部 5 个 Agent。"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# API Key 从 .env 文件读取，请复制 .env.example 为 .env 并填入你的 Key
from dotenv import load_dotenv; load_dotenv(override=True)

from app.core.state import create_initial_state
from app.core.workflow import get_orchestrator

orchestrator = get_orchestrator()
state = create_initial_state(
    problem_raw="某工厂生产A、B两种产品，每件A利润40元，耗材2kg，工时3h；每件B利润30元，耗材3kg，工时2h。每天可用材料120kg，工时100h。求最大利润的生产方案。",
    mode="execute",
    session_id="e2e_test",
)

print("=" * 60)
print("全流程测试: 分析 -> 建模 -> 求解 -> 验证 -> 写作")
print("=" * 60)

result = orchestrator.invoke(state, {"recursion_limit": 50})

print()
print(f"问题类型: {result.get('problem_type')}")
print(f"执行计划: {' -> '.join(result.get('execution_plan', []))}")
print(f"KB 方法: {len(result.get('kb_methods', []))} 个")
print()
print(f"[分析Agent] 输出: {len(result.get('analysis_output',''))} 字")
print(f"[建模Agent] 输出: {len(result.get('model_output',''))} 字")
print(f"[求解Agent] 输出: {len(result.get('solving_output',''))} 字")
print(f"[验证Agent] 输出: {len(result.get('verification_output',''))} 字, 判定: {'PASS' if result.get('verification_passed') else 'FAIL'}")
print(f"[写作Agent] 输出: {len(result.get('writing_output',''))} 字")
print(f"[最终] 总输出: {len(result.get('final_response',''))} 字")
print()

# 保存论文
paper = result.get("writing_output", "")
if paper:
    with open("output_paper.md", "w", encoding="utf-8") as f:
        f.write(paper)
    print("论文已保存到 output_paper.md")
