"""Планировщик агента: команда оператора → задания (Трек B7).

Пример команды: «заведи 3 аккаунта на kwork» → список заданий, которые
исполняются через AccountRegistrar (dry-run провайдеры по умолчанию).
"""
from __future__ import annotations

import re

from src.observability import get_logger
from src.platforms.registry import _REGISTRY
from src.provisioning.registrar import AccountRegistrar

logger = get_logger("autofl.agent")

_COMMAND_RE = re.compile(
    r"завед(?:и|ите)?\s+(?P<count>\d+)\s+аккаунт(?:а|ов|ы)?"
    r"(?:\s+(?:на|для|для площадк(?:и|и)))?\s*(?P<platform>\w+)",
    re.IGNORECASE,
)

MAX_ACCOUNTS_PER_COMMAND = 20


class AgentPlanner:
    """Декомпозиция NL-команд в задания и их исполнение."""

    def __init__(self, registrar: AccountRegistrar | None = None) -> None:
        self._registrar = registrar or AccountRegistrar()

    async def plan(self, command: str) -> list[dict]:
        """Разбирает команду; возвращает список запланированных заданий."""
        m = _COMMAND_RE.search(command)
        if not m:
            raise ValueError(f"Не удалось разобрать команду: {command!r}")
        count = int(m.group("count"))
        platform = m.group("platform").lower()
        if platform not in _REGISTRY:
            raise ValueError(
                f"Неизвестная площадка: {platform!r}. Доступны: "
                f"{', '.join(sorted(_REGISTRY))}"
            )
        if not 1 <= count <= MAX_ACCOUNTS_PER_COMMAND:
            raise ValueError(
                f"Число аккаунтов должно быть от 1 до {MAX_ACCOUNTS_PER_COMMAND}"
            )
        return [
            {"platform": platform, "index": i + 1, "status": "planned"}
            for i in range(count)
        ]

    async def execute(self, command: str) -> list[dict]:
        """Планирует задания и выполняет регистрации."""
        jobs = await self.plan(command)
        results: list[dict] = []
        for job in jobs:
            logger.info(
                "Задание %s/%s: регистрация на %s",
                job["index"],
                len(jobs),
                job["platform"],
            )
            account = await self._registrar.register(job["platform"])
            results.append({**job, "status": "done", "account": account})
        return results

