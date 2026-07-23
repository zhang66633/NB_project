import asyncio
from app.api.tasks import _run_orchestrator_sync

async def test():
    print("Spawning...")
    task = asyncio.create_task(
        asyncio.to_thread(_run_orchestrator_sync, "test_001", 
            "某工厂生产A、B两种产品，每件A产品需原料2kg、工时3h、利润100元，每件B产品需原料3kg、工时2h、利润80元。现有原料50kg、工时48h。求使利润最大化的生产方案。",
            "execute", "guest")
    )
    print("Spawned, waiting 5s...")
    await asyncio.sleep(5)
    print("Done waiting")

asyncio.run(test())
