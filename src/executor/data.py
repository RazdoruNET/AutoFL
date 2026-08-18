"""Исполнитель задач по обработке данных (Этап 6).

Парсинг, преобразование форматов, таблицы, дедупликация данных.
"""
from src.brain.classifier import TaskCategory
from src.brain.prompts import DATA_EXECUTOR_SYSTEM_PROMPT
from src.executor.base import Deliverable, Executor


class DataExecutor(Executor):
    """Обработка данных по ТЗ (LLM + детерминированные преобразования)."""

    category = TaskCategory.DATA

    def __init__(self, llm_client) -> None:
        self._llm = llm_client
        self._system_prompt = DATA_EXECUTOR_SYSTEM_PROMPT

    async def run(
        self,
        task_title: str,
        task_description: str,
        client_context: str = "",
    ) -> Deliverable:
        # Этап 6: детерминированные преобразования + LLM для сложных шагов.
        raise NotImplementedError("Этап 6: DataExecutor.run")
