"""Адаптер YouDo (Этап 3). Playwright-контур без публичного API.

Заготовка. Реализация методов — в Этапах 3–4 и 7.
"""
from src.platforms.base import (
    PlatformAdapter,
    SubmissionResult,
    TaskCandidate,
)


class YouDoAdapter(PlatformAdapter):
    slug = "youdo"

    async def discover(self) -> list[TaskCandidate]:
        raise NotImplementedError("Этап 4: поиск заданий")

    async def apply(self, candidate: TaskCandidate) -> bool:
        raise NotImplementedError("Этап 7: отклик на задание")

    async def submit(
        self, candidate: TaskCandidate, deliverable: str
    ) -> SubmissionResult:
        raise NotImplementedError("Этап 7: отправка результата")

    async def send_message(self, candidate: TaskCandidate, text: str) -> bool:
        raise NotImplementedError("Этап 7: переписка с заказчиком")
