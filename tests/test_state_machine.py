"""Машина состояний: переходы, запреты, идемпотентность (Этап 7)."""
import pytest

from src.workflow.state_machine import (
    TaskStatus,
    TransitionError,
    apply_transition,
    can_transition,
)


def test_happy_path_to_paid():
    status = TaskStatus.DISCOVERED
    path = [
        TaskStatus.CLASSIFIED,
        TaskStatus.QUEUED,
        TaskStatus.APPROVED,
        TaskStatus.APPLIED,
        TaskStatus.EXECUTING,
        TaskStatus.QUALITY_CHECK,
        TaskStatus.READY,
        TaskStatus.SUBMITTED,
        TaskStatus.DELIVERED,
        TaskStatus.DONE,
        TaskStatus.PAID,
    ]
    for target in path:
        status = apply_transition(status, target)
    assert status == TaskStatus.PAID


def test_reject_path():
    status = apply_transition(TaskStatus.DISCOVERED, TaskStatus.CLASSIFIED)
    status = apply_transition(status, TaskStatus.REJECTED)
    assert status == TaskStatus.REJECTED


def test_revision_loop_back_to_executing():
    status = apply_transition(TaskStatus.SUBMITTED, TaskStatus.REVISION_REQUESTED)
    status = apply_transition(status, TaskStatus.EXECUTING)
    assert status == TaskStatus.EXECUTING


def test_payment_flow_prepaid():
    """Трек B9: переговоры → предоплата на карту → выполнение."""
    status = apply_transition(TaskStatus.APPLIED, TaskStatus.NEGOTIATING)
    status = apply_transition(status, TaskStatus.AWAITING_PAYMENT)
    status = apply_transition(status, TaskStatus.PAID)
    status = apply_transition(status, TaskStatus.EXECUTING)
    assert status == TaskStatus.EXECUTING


def test_payment_flow_on_delivery():
    """Трек B9: сдали работу → ждём оплату на карту → PAID."""
    status = apply_transition(TaskStatus.SUBMITTED, TaskStatus.AWAITING_PAYMENT)
    status = apply_transition(status, TaskStatus.PAID)
    assert status == TaskStatus.PAID


def test_negotiation_cancel_is_allowed():
    assert can_transition(TaskStatus.NEGOTIATING, TaskStatus.CANCELLED)
    status = apply_transition(TaskStatus.NEGOTIATING, TaskStatus.CANCELLED)
    assert status == TaskStatus.CANCELLED


def test_invalid_transition_raises():
    with pytest.raises(TransitionError):
        apply_transition(TaskStatus.DISCOVERED, TaskStatus.PAID)
    assert not can_transition(TaskStatus.QUEUED, TaskStatus.EXECUTING)


def test_idempotent_terminal_restart():
    # восстановление после краша в терминальном статусе не падает
    assert apply_transition(TaskStatus.CANCELLED, TaskStatus.CANCELLED) == TaskStatus.CANCELLED
    assert apply_transition(TaskStatus.REJECTED, TaskStatus.REJECTED) == TaskStatus.REJECTED
    # но не-терминальный переход в себя — ошибка
    with pytest.raises(TransitionError):
        apply_transition(TaskStatus.READY, TaskStatus.READY)
    with pytest.raises(TransitionError):
        apply_transition(TaskStatus.PAID, TaskStatus.PAID)  # PAID не терминальный
