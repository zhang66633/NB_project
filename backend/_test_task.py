import traceback, asyncio
from app.core.workflow import build_orchestrator
from app.core.state import AgentState

async def main():
    state: AgentState = {
        "messages": [],
        "mode": "execute",
        "session_id": "test_001",
        "problem_raw": (
            "某工厂生产A、B两种产品，每件A产品需原料2kg、工时3h、利润100元，"
            "每件B产品需原料3kg、工时2h、利润80元。现有原料50kg、工时48h。"
            "求使利润最大化的生产方案。"
        ),
        "problem_type": "",
        "problem_complexity": "simple",
        "data_dependency": "theoretical",
        "kb_methods": [], "kb_papers": [], "kb_templates": [],
        "execution_plan": [],
        "current_step_index": 0,
        "retry_count": 0, "max_retries": 3,
        "analysis_output": None, "model_output": None,
        "solving_output": None, "verification_output": None,
        "writing_output": None,
        "verification_passed": None, "verification_feedback": None,
        "rollback_target": None,
        "progress_events": [],
    }
    orch = build_orchestrator()
    async for event in orch.astream(state, stream_mode="updates"):
        print(f"Event: {list(event.keys())}")
    print("Done!")

try:
    asyncio.run(main())
except Exception:
    traceback.print_exc()
