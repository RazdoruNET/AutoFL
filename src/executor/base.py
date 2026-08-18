"""Интерфейс исполнителей заданий (Этап 6)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.brain.classifier import TaskCategory


@dataclass
class Deliverable:
    content: str
    format: str = "text"


class Executor(ABC):
    """Исполнитель: ТЗ → готовый результат (черновик)."""

    category: TaskCategory = TaskCategory.OTHER

    @abstractmethod
    async def run(
        self,
        task_title: str,
        task_description: str,
        client_context: str = "",
    ) -> Deliverable:
        """Производит результат по требованиям задания."""
