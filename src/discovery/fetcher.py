"""Сбор ленты заданий с площадки (Этап 4).

Заготовка. Работает поверх PlatformAdapter.discover(): применяет rate-limit,
дедупликацию и сохраняет новые задания в таблицу candidates.
"""
import asyncio

from src.discovery.dedupe import CandidateDedupe
from src.observability import get_logger
from src.platforms.base import PlatformAdapter, TaskCandidate

logger = get_logger("autofl.discovery")


class DiscoveryFetcher:
    """Оркестрирует сбор заданий с одного адаптера площадки."""

    def __init__(
        self,
        adapter: PlatformAdapter,
        rate_limit_seconds: int = 30,
        dedupe: CandidateDedupe | None = None,
    ) -> None:
        self._adapter = adapter
        self._rate_limit = max(rate_limit_seconds, 5)
        self._dedupe = dedupe or CandidateDedupe()

    async def fetch_new(self) -> list[TaskCandidate]:
        """Один проход по ленте: возвращает только новые задания.

        Полная реализация (пагинация, фильтры, обработка вылета сессии) —
        в Этапе 4.
        """
        raise NotImplementedError("Этап 4: fetch_new — реализация сбора ленты")
