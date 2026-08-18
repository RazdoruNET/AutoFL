"""Исполнитель кода — только через песочницу (Этап 6).

Задания «напиши скрипт» выполняются изолированно: без сети, с лимитами
времени и памяти. См. src/sandbox/runner.py.
"""
from src.brain.classifier import TaskCategory
from src.executor.base import Deliverable, Executor
from src.sandbox.runner import run_code_in_sandbox


class CodeExecutor(Executor):
    """Извлечение кода из ТЗ, запуск в песочнице, сборка результата."""

    category = TaskCategory.CODE

    async def run(
        self,
        task_title: str,
        task_description: str,
        client_context: str = "",
    ) -> Deliverable:
        # Этап 6: извлечь код из ТЗ, запустить в песочнице, собрать ответ.
        raise NotImplementedError("Этап 6: CodeExecutor.run")
