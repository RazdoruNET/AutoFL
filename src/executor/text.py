"""Текстовые исполнители: рерайт, перевод, описание, отзыв, SEO (Этап 6)."""
from src.brain.classifier import TaskCategory
from src.brain.prompts import TEXT_EXECUTOR_SYSTEM_PROMPT
from src.executor.base import Deliverable, Executor


class TextExecutor(Executor):
    """Генерация текста по ТЗ через LLM (рерайт/перевод/описание и т.п.)."""

    category = TaskCategory.TEXT

    def __init__(self, llm_client) -> None:
        self._llm = llm_client
        self._system_prompt = TEXT_EXECUTOR_SYSTEM_PROMPT

    async def run(
        self,
        task_title: str,
        task_description: str,
        client_context: str = "",
    ) -> Deliverable:
        # Этап 6: вызов LLM, сборка результата, обрезка по лимиту длины.
        raise NotImplementedError("Этап 6: TextExecutor.run")
