"""Сборка реквизитов оплаты для заказчика (Трек B1).

Полный PAN хранится только зашифрованным (FundingSource.pan_enc).
Заказчику передаётся СБП-номер (предпочтительно) или замаскированная карта.
Текст — человечный, без «машинных» маркеров.
"""
from dataclasses import dataclass


@dataclass
class PaymentRequisites:
    preferred_kind: str = "sbp"  # sbp | card
    holder: str = ""
    bank: str = ""
    sbp_phone: str = ""
    card_masked: str = ""


def build_requisites_text(r: PaymentRequisites) -> str:
    """Собирает текст с реквизитами для отправки заказчику."""
    parts: list[str] = []
    if r.preferred_kind == "sbp" and r.sbp_phone:
        parts.append(f"СБП по номеру {r.sbp_phone}")
    elif r.card_masked:
        parts.append(f"карта {r.card_masked}")
    if r.holder:
        parts.append(f"получатель {r.holder}")
    if r.bank:
        parts.append(f"банк {r.bank}")
    if not parts:
        return "Реквизиты для перевода уточню отдельно."
    return "Перевести можно: " + ", ".join(parts) + "."

