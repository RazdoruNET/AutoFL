"""Верификация прихода оплаты на карту/СБП (Трек B1)."""
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional


@dataclass
class PaymentEvidence:
    amount: float
    ref: str = ""
    note: str = ""


ConfirmCallback = Callable[[float, Optional[PaymentEvidence]], Awaitable[bool]]


class PaymentVerifier:
    """Подтверждает поступление оплаты.

    Режимы (PAYMENT_VERIFICATION_MODE):
      manual — оператор подтверждает через админ-бот (callable inject);
      bank_sms — сверка суммы по evidence (парсинг уведомлений — Этап B9).
    """

    def __init__(
        self,
        mode: str = "manual",
        confirm_cb: Optional[ConfirmCallback] = None,
    ) -> None:
        self._mode = mode
        self._confirm = confirm_cb

    def set_confirmation_callback(self, cb: ConfirmCallback) -> None:
        self._confirm = cb

    async def verify(
        self,
        expected_amount: float,
        evidence: Optional[PaymentEvidence] = None,
    ) -> bool:
        if self._mode == "manual":
            if self._confirm is None:
                raise RuntimeError("Не настроен канал подтверждения оплаты оператором")
            return await self._confirm(expected_amount, evidence)
        if self._mode == "bank_sms":
            if evidence is None:
                return False
            # Базовая сверка суммы; парсинг банковских уведомлений — Этап B9.
            return abs(evidence.amount - expected_amount) < 0.01
        raise ValueError(f"Неизвестный режим верификации оплаты: {self._mode}")
