"""Контроллер расходов: бюджет + порог авто-трат (Трек B1)."""
from dataclasses import dataclass

from src.finance.budget import BudgetPolicy


@dataclass
class SpendingDecision:
    approved: bool
    auto: bool  # True — авто-трата без подтверждения оператора
    reason: str = ""


class SpendingController:
    """Решает, можно ли потратить amount по категории и нужен ли аппрув."""

    def __init__(
        self,
        budget: BudgetPolicy,
        auto_limit_rub: float = 200.0,
        approval_required: bool = True,
    ) -> None:
        self._budget = budget
        self._auto_limit = auto_limit_rub
        self._approval_required = approval_required

    def decide(self, category: str, amount: float) -> SpendingDecision:
        if not self._budget.allow(category, amount):
            return SpendingDecision(
                False, False, f"превышен лимит категории {category}"
            )
        if self._approval_required or amount > self._auto_limit:
            return SpendingDecision(True, False, "требуется подтверждение оператора")
        return SpendingDecision(True, True, "авто-трата в рамках лимита")
