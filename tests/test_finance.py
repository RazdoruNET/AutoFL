"""Финансы агента: ledger, бюджет, контроль расходов (Трек B1)."""
from src.finance.budget import BudgetPolicy
from src.finance.spending import SpendingController
from src.finance.wallet import LedgerEntry, WalletLedger


def test_wallet_balance_and_categories():
    w = WalletLedger()
    w.record(LedgerEntry(500, "income", "payment_income"))
    w.record(LedgerEntry(120, "expense", "captcha"))
    w.record(LedgerEntry(50, "expense", "email"))
    assert w.balance() == 330.0
    assert w.by_category("captcha") == 120.0
    assert w.total("income") == 500.0
    assert w.total("expense") == 170.0


def test_budget_category_limit():
    b = BudgetPolicy(category_limits={"captcha": 100.0})
    assert b.allow("captcha", 50.0)
    assert not b.allow("captcha", 150.0)
    assert b.allow("registration", 999.0)  # категория без лимита — разрешено


def test_spending_auto_within_limit():
    c = SpendingController(BudgetPolicy(), auto_limit_rub=200.0, approval_required=False)
    d = c.decide("captcha", 50.0)
    assert d.approved and d.auto


def test_spending_needs_approval_above_limit():
    c = SpendingController(BudgetPolicy(), auto_limit_rub=200.0, approval_required=False)
    d = c.decide("captcha", 500.0)
    assert d.approved and not d.auto


def test_spending_approval_required_mode():
    c = SpendingController(BudgetPolicy(), approval_required=True)
    d = c.decide("captcha", 10.0)
    assert d.approved and not d.auto


def test_spending_rejected_by_budget():
    b = BudgetPolicy(category_limits={"captcha": 100.0})
    c = SpendingController(b, approval_required=False)
    d = c.decide("captcha", 300.0)
    assert not d.approved
