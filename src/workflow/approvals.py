"""Гейты одобрения — human-in-the-loop (Этап 8).

По умолчанию любое внешнее действие (отклик, отправка, сообщение, запуск кода)
требует одобрения оператора, пока AUTO_EXECUTE не включён явно.
"""
from dataclasses import dataclass, field
from enum import Enum

from src.config.settings import get_settings


class ActionType(str, Enum):
    APPLY = "apply"
    SUBMIT = "submit"
    MESSAGE = "message"
    CODE_RUN = "code_run"


@dataclass
class ApprovalRequest:
    action: ActionType
    task_id: int
    summary: str
    payload: dict = field(default_factory=dict)


@dataclass
class ApprovalDecision:
    approved: bool
    comment: str = ""


class ApprovalGate:
    """Проверяет необходимость одобрения и запрашивает его у оператора."""

    def __init__(self, notifier=None) -> None:
        self._notifier = notifier  # Telegram-админ (Этап 8)

    def requires_approval(self, action: ActionType) -> bool:
        settings = get_settings()
        if settings.dry_run:
            return True
        if not settings.auto_execute:
            return True
        return settings.approval_required

    async def request(self, req: ApprovalRequest) -> ApprovalDecision:
        """Отправка запроса оператору и ожидание решения.

        Полный контур (кнопки approve/reject в админ-боте) — Этап 8.
        """
        raise NotImplementedError("Этап 8: ApprovalGate.request")
