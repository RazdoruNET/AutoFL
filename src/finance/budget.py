"""Политика расходов: лимиты по категориям и суточный лимит (Трек B1)."""
from dataclasses import dataclass, field


@dataclass
class BudgetPolicy:
    # {категория: макс. сумма за операцию, руб.}
    category_limits: dict[str, float] = field(default_factory=dict)
    daily_limit: float = 0.0  # 0 — без лимита

    def allow(self, category: str, amount: float) -> bool:
        limit = self.category_limits.get(category)
        if limit is not None and amount > limit:
            return False
        if self.daily_limit > 0 and amount > self.daily_limit:
            return False
        return True
