"""LLM-классификатор заданий (Этап 5).

Возвращает структурированный вердикт через pydantic. Подключение реального
LLM-клиента — в Этапе 5; в тестах используется мок.
"""
from enum import Enum

from pydantic import BaseModel, Field


class TaskCategory(str, Enum):
    TEXT = "text"
    DATA = "data"
    CODE = "code"
    OTHER = "other"
    UNSUPPORTED = "unsupported"


class Complexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    HARD = "hard"


class ClassifierVerdict(BaseModel):
    category: TaskCategory = TaskCategory.OTHER
    complexity: Complexity = Complexity.SIMPLE
    doable: bool = False
    safety_score: float = Field(ge=0.0, le=1.0, default=0.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    reasons: list[str] = Field(default_factory=list)


class TaskClassifier:
    """Обёртка над LLM: текст задания → ClassifierVerdict."""

    def __init__(self, llm_client) -> None:
        self._llm = llm_client

    async def classify(self, title: str, description: str) -> ClassifierVerdict:
        # Этап 5: вызов LLM с pydantic-структурой вывода.
        raise NotImplementedError("Этап 5: подключение LLM-классификатора")
