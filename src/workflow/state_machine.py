"""Машина состояний задачи (Этап 7).

Переходы атомарны и идемпотентны: повторный вызов с тем же текущим
состоянием в терминальном статусе не приводит к двойному действию.
"""
from enum import Enum


class TaskStatus(str, Enum):
    DISCOVERED = "discovered"
    CLASSIFIED = "classified"
    REJECTED = "rejected"
    QUEUED = "queued"
    APPROVED = "approved"
    APPLIED = "applied"
    NEGOTIATING = "negotiating"  # Трек B9: обсуждение условий и оплаты
    AWAITING_PAYMENT = "awaiting_payment"  # Трек B9: ждём приход на карту
    PAID = "paid"  # Трек B9: оплата поступила
    EXECUTING = "executing"
    QUALITY_CHECK = "quality_check"
    READY = "ready"
    SUBMITTED = "submitted"
    DELIVERED = "delivered"
    REVISION_REQUESTED = "revision_requested"
    DONE = "done"
    CANCELLED = "cancelled"


TERMINAL: set[TaskStatus] = {TaskStatus.REJECTED, TaskStatus.CANCELLED}

ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.DISCOVERED: {TaskStatus.CLASSIFIED},
    TaskStatus.CLASSIFIED: {TaskStatus.REJECTED, TaskStatus.QUEUED},
    TaskStatus.QUEUED: {TaskStatus.APPROVED, TaskStatus.CANCELLED},
    TaskStatus.APPROVED: {TaskStatus.APPLIED, TaskStatus.CANCELLED},
    TaskStatus.APPLIED: {TaskStatus.EXECUTING, TaskStatus.NEGOTIATING, TaskStatus.CANCELLED},
    # Трек B9: после отклика — переговоры по условиям и оплате
    TaskStatus.NEGOTIATING: {
        TaskStatus.AWAITING_PAYMENT,  # согласились, ждём предоплату на карту
        TaskStatus.READY,             # схема on_delivery — выполняем без предоплаты
        TaskStatus.CANCELLED,
    },
    TaskStatus.AWAITING_PAYMENT: {TaskStatus.PAID, TaskStatus.CANCELLED},
    TaskStatus.PAID: {TaskStatus.EXECUTING, TaskStatus.CANCELLED},
    TaskStatus.EXECUTING: {TaskStatus.QUALITY_CHECK, TaskStatus.CANCELLED},
    TaskStatus.QUALITY_CHECK: {
        TaskStatus.READY,
        TaskStatus.EXECUTING,  # повторная генерация после неудачной проверки
        TaskStatus.CANCELLED,
    },
    TaskStatus.READY: {TaskStatus.SUBMITTED, TaskStatus.CANCELLED},
    TaskStatus.SUBMITTED: {
        TaskStatus.DELIVERED,
        TaskStatus.REVISION_REQUESTED,
        TaskStatus.AWAITING_PAYMENT,  # on_delivery: сдали работу, ждём оплату
        TaskStatus.CANCELLED,
    },
    TaskStatus.REVISION_REQUESTED: {
        TaskStatus.EXECUTING,
        TaskStatus.DELIVERED,  # заказчик согласился без правок
        TaskStatus.CANCELLED,
    },
    TaskStatus.DELIVERED: {
        TaskStatus.DONE,
        TaskStatus.AWAITING_PAYMENT,  # on_delivery: оплата после получения
        TaskStatus.CANCELLED,
    },
    TaskStatus.DONE: {TaskStatus.AWAITING_PAYMENT, TaskStatus.PAID},
    TaskStatus.REJECTED: set(),
    TaskStatus.CANCELLED: set(),
}


class TransitionError(ValueError):
    """Недопустимый переход состояния задачи."""


def can_transition(current: TaskStatus, target: TaskStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def apply_transition(current: TaskStatus, target: TaskStatus) -> TaskStatus:
    """Проверяет и применяет переход; возвращает новое состояние.

    Идемпотентность: повторный переход терминального состояния в само себя
    считается успешным (восстановление после краша).
    """
    if current == target and current in TERMINAL:
        return current
    if not can_transition(current, target):
        raise TransitionError(f"Недопустимый переход: {current.value} → {target.value}")
    return target
