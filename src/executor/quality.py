"""Самопроверка результата перед отправкой (Этап 6)."""
from dataclasses import dataclass, field


@dataclass
class QualityVerdict:
    ok: bool
    score: float
    issues: list[str] = field(default_factory=list)


class QualityChecker:
    """Проверяет соответствие результата требованиям ТЗ.

    Детерминированные проверки (объём, ключевые требования ТЗ) + LLM-оценка.
    Регенерация ограничена (bounded); при исчерпании — эскалация оператору.
    """

    def __init__(self, llm_client=None, max_regenerations: int = 1) -> None:
        self._llm = llm_client
        self._max_regens = max_regenerations

    async def check(self, task_description: str, deliverable: str) -> QualityVerdict:
        # Этап 6: self-eval перед отправкой.
        raise NotImplementedError("Этап 6: QualityChecker.check")
