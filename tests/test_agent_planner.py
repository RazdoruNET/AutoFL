"""Планировщик агента: разбор команд и исполнение (Трек B7)."""
import pytest

from src.agent.planner import AgentPlanner


class FakeRegistrar:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def register(self, platform: str) -> dict:
        self.calls.append(platform)
        return {"account_id": len(self.calls), "login": f"{platform}@dry.local"}


async def test_plan_parses_command():
    planner = AgentPlanner(registrar=FakeRegistrar())
    jobs = await planner.plan("заведи 3 аккаунта на kwork")
    assert len(jobs) == 3
    assert all(j["platform"] == "kwork" for j in jobs)
    assert all(j["status"] == "planned" for j in jobs)


async def test_plan_accepts_variants():
    planner = AgentPlanner(registrar=FakeRegistrar())
    jobs = await planner.plan("Заведите 2 аккаунта для flru")
    assert len(jobs) == 2
    assert jobs[0]["platform"] == "flru"


async def test_plan_unknown_platform_raises():
    planner = AgentPlanner(registrar=FakeRegistrar())
    with pytest.raises(ValueError, match="Неизвестная площадка"):
        await planner.plan("заведи 1 аккаунт на upwork")


async def test_plan_bad_command_raises():
    planner = AgentPlanner(registrar=FakeRegistrar())
    with pytest.raises(ValueError, match="разобрать команду"):
        await planner.plan("сделай что-нибудь")


async def test_execute_runs_all_jobs():
    registrar = FakeRegistrar()
    planner = AgentPlanner(registrar=registrar)
    results = await planner.execute("заведи 2 аккаунта на youdo")
    assert len(results) == 2
    assert registrar.calls == ["youdo", "youdo"]
    assert all(r["status"] == "done" for r in results)
    assert all(r["account"]["account_id"] for r in results)
