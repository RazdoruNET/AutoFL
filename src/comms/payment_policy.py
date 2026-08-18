"""Политика приёма оплаты (Трек B9)."""
from enum import Enum


class PaymentPolicyMode(str, Enum):
    CARD_REQUIRED = "card_required"  # настаивать на оплате на карту/СБП
    CARD_PREFERRED = "card_preferred"  # предлагать карту, при отказе — сделка площадки


class PaymentScheme(str, Enum):
    ADVANCE = "advance"  # 100% предоплата
    PARTIAL_ADVANCE = "partial_advance"  # частичная предоплата
    ON_DELIVERY = "on_delivery"  # оплата после выполнения


class PaymentPolicy:
    """Режим настаивания на карту и схема оплаты."""

    def __init__(
        self,
        mode: PaymentPolicyMode,
        scheme: PaymentScheme,
        advance_fraction: float = 0.5,
    ) -> None:
        self.mode = mode
        self.scheme = scheme
        self.advance_fraction = advance_fraction

    @classmethod
    def from_settings(cls) -> "PaymentPolicy":
        from src.config.settings import get_settings

        s = get_settings()
        return cls(
            mode=PaymentPolicyMode(s.payment_policy),
            scheme=PaymentScheme(s.payment_scheme),
        )

    def insist_on_card(self) -> bool:
        """True — отказываться от безопасной сделки и настаивать на карту."""
        return self.mode == PaymentPolicyMode.CARD_REQUIRED

    def initial_advance(self, price: float) -> float:
        """Сумма предоплаты для выбранной схемы оплаты."""
        if self.scheme == PaymentScheme.ADVANCE:
            return price
        if self.scheme == PaymentScheme.PARTIAL_ADVANCE:
            return round(price * self.advance_fraction, 2)
        return 0.0
