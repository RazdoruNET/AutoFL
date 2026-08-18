"""Единый интерфейс адаптеров фриланс-площадок (Этап 3)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TaskCandidate:
    """Задание из ленты площадки до принятия в работу."""

    platform: str
    external_id: str
    url: str
    title: str
    description: str = ""
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[str] = None
    raw: dict = field(default_factory=dict)


@dataclass
class SubmissionResult:
    ok: bool
    submission_id: Optional[str] = None
    error: str = ""


class PlatformAdapter(ABC):
    """Базовый адаптер. Каждая площадка реализует свой класс.

    Реализации: kwork.py, flru.py, youdo.py. Выбор — через registry.
    """

    slug: str = ""

    @abstractmethod
    async def discover(self) -> list[TaskCandidate]:
        """Новые задания из ленты (Этап 4)."""

    @abstractmethod
    async def apply(self, candidate: TaskCandidate) -> bool:
        """Отклик/заявка на задание (Этап 7)."""

    @abstractmethod
    async def submit(
        self, candidate: TaskCandidate, deliverable: str
    ) -> SubmissionResult:
        """Отправка результата заказчику."""

    @abstractmethod
    async def send_message(self, candidate: TaskCandidate, text: str) -> bool:
        """Сообщение заказчику (уточнения, сопровождение)."""
