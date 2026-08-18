"""Оркестратор цикла: discover → classify → approve → execute → submit.

Полная реализация связывает discovery, brain, workflow и executor (Этап 7).
"""
from src.observability import get_logger

logger = get_logger("autofl.pipeline")


class Pipeline:
    """Последовательный конвейер обработки заданий."""

    async def run_once(self) -> int:
        """Один проход цикла; возвращает число обработанных заданий.

        Идемпотентность обеспечивает state_machine: повторный запуск после
        краша продолжает с сохранённого статуса задачи.
        """
        raise NotImplementedError("Этап 7: Pipeline.run_once")
