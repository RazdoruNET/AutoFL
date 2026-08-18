"""Демо: оператор командует — система регистрирует аккаунты (dry-run)."""
import asyncio

from src.agent.planner import AgentPlanner


async def main() -> None:
    planner = AgentPlanner()
    command = "заведи 2 аккаунта на kwork"
    print(f"КОМАНДА ОПЕРАТОРА: {command!r}\n")

    jobs = await planner.plan(command)
    print("ПЛАН:")
    for j in jobs:
        print(f"  #{j['index']}  platform={j['platform']}  status={j['status']}")

    print("\nВЫПОЛНЕНИЕ (dry-run провайдеры: почта/SMS/капча):")
    results = await planner.execute(command)
    for r in results:
        acc = r["account"]
        print(
            f"  #{r['index']} {r['platform']}: account_id={acc['account_id']} "
            f"login={acc['login']} phone={acc['phone']}"
        )
    print(f"\nИТОГ: создано аккаунтов — {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
