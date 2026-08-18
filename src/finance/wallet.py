"""Ledger средств агента: доходы и расходы (Трек B1).

In-memory-реализация для логики и тестов; в проде записи сохраняются
в таблицу Transaction (src/db/models.py).
"""
from dataclasses import dataclass


@dataclass
class LedgerEntry:
    amount: float
    direction: str  # income | expense
    category: str
    ref: str = ""


class WalletLedger:
    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    def record(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def balance(self) -> float:
        return self.total("income") - self.total("expense")

    def total(self, direction: str) -> float:
        return sum(e.amount for e in self._entries if e.direction == direction)

    def by_category(self, category: str) -> float:
        return sum(e.amount for e in self._entries if e.category == category)
