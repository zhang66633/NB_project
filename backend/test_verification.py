"""测试验证 Agent。"""
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ["DEEPSEEK_API_KEY"] = "YOUR_DEEPSEEK_KEY_HERE"
os.environ["OPENAI_API_KEY"] = "YOUR_DEEPSEEK_KEY_HERE"
from dotenv import load_dotenv; load_dotenv(override=True)

from app.core.state import create_initial_state
from app.core.workflow import get_orchestrator

orchestrator = get_orchestrator()
state = create_initial_state(
    problem_raw="某工厂生产A、B两种产品，每件A利润40元，耗材2kg，工时3小时；每件B利润30元，耗材3kg，工时2小时。每天可用材料120kg，工时100小时。求最大利润的生产方案。",
    mode="execute",
    session_id="test9",
)

result = orchestrator.invoke(state, {"recursion_limit": 50})

print("验证结果:", "PASS" if result.get("verification_passed") else "FAIL")
print("回退目标:", result.get("rollback_target"))
print("重试次数:", result.get("retry_count"))
print()
print("===== 验证 Agent 输出 =====")
print(result.get("verification_output", "无")[:2500])
