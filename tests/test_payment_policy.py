"""Политика приёма оплаты и переговоры (Трек B9)."""
import random

from src.comms.negotiation import NegotiationScript
from src.comms.payment_policy import (
    PaymentPolicy,
    PaymentPolicyMode,
    PaymentScheme,
)
from src.finance.requisites import PaymentRequisites, build_requisites_text


def test_card_required_insists():
    p = PaymentPolicy(PaymentPolicyMode.CARD_REQUIRED, PaymentScheme.ADVANCE)
    assert p.insist_on_card()
    assert p.initial_advance(1000) == 1000.0


def test_card_preferred_does_not_insist():
    p = PaymentPolicy(PaymentPolicyMode.CARD_PREFERRED, PaymentScheme.ON_DELIVERY)
    assert not p.insist_on_card()
    assert p.initial_advance(1000) == 0.0


def test_partial_advance():
    p = PaymentPolicy(
        PaymentPolicyMode.CARD_REQUIRED,
        PaymentScheme.PARTIAL_ADVANCE,
        advance_fraction=0.5,
    )
    assert p.initial_advance(1000) == 500.0


def test_from_settings():
    p = PaymentPolicy.from_settings()
    assert isinstance(p.mode, PaymentPolicyMode)
    assert isinstance(p.scheme, PaymentScheme)


def test_requisites_sbp_text():
    r = PaymentRequisites(
        preferred_kind="sbp",
        holder="Иван",
        bank="Банк",
        sbp_phone="+79000000000",
    )
    text = build_requisites_text(r)
    assert "+79000000000" in text
    assert "Иван" in text
    assert "Банк" in text


def test_negotiation_card_required():
    policy = PaymentPolicy(PaymentPolicyMode.CARD_REQUIRED, PaymentScheme.ADVANCE)
    req = PaymentRequisites(preferred_kind="sbp", sbp_phone="+79000000000", holder="Иван")
    script = NegotiationScript(policy, req, rng=random.Random(1))
    assert "1 000 ₽" in script.terms_message(1000)
    assert "+7 (900) 000-00-00" in script.requisites_message()
    objection = script.handle_safe_deal_objection()
    assert "прям" in objection  # все варианты упоминают прямые переводы


def test_negotiation_card_preferred_yields():
    policy = PaymentPolicy(PaymentPolicyMode.CARD_PREFERRED, PaymentScheme.ON_DELIVERY)
    script = NegotiationScript(policy, PaymentRequisites(), rng=random.Random(2))
    assert "сделк" in script.handle_safe_deal_objection()


def test_negotiation_partial_advance_mentions_amount():
    policy = PaymentPolicy(
        PaymentPolicyMode.CARD_REQUIRED,
        PaymentScheme.PARTIAL_ADVANCE,
        advance_fraction=0.5,
    )
    req = PaymentRequisites(preferred_kind="sbp", sbp_phone="+79000000000", holder="Иван")
    script = NegotiationScript(policy, req, rng=random.Random(3))
    terms = script.terms_message(2000)
    assert "2 000 ₽" in terms
    assert "1 000 ₽" in terms  # предоплата 50%


def test_requisites_phone_human_format():
    req = PaymentRequisites(preferred_kind="sbp", sbp_phone="89001234567", holder="Пётр")
    script = NegotiationScript(
        PaymentPolicy(PaymentPolicyMode.CARD_REQUIRED, PaymentScheme.ADVANCE),
        req,
        rng=random.Random(0),
    )
    assert "+7 (900) 123-45-67" in script.requisites_message()


def test_messages_vary_across_rng():
    """Один сценарий даёт разные формулировки — переписка не выглядит шаблонной."""
    policy = PaymentPolicy(PaymentPolicyMode.CARD_REQUIRED, PaymentScheme.ADVANCE)
    req = PaymentRequisites(preferred_kind="sbp", sbp_phone="+79000000000", holder="Иван")
    outputs = {
        NegotiationScript(policy, req, rng=random.Random(seed)).terms_message(1000)
        for seed in range(8)
    }
    assert len(outputs) > 1
