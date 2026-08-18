"""Переговоры при заключении заказа (Трек B9).

Сообщения генерируются по шаблонам живой речи: на каждый случай — несколько
вариантов и случайный выбор, чтобы переписка не выглядела однотипной и не
выдавала автоматизацию. Для заказчика — никаких «машинных» маркеров вроде
нумерованных списков и структурированных строк.
"""
import random
import re

from src.comms.payment_policy import PaymentPolicy
from src.finance.requisites import PaymentRequisites


def _format_phone(phone: str) -> str:
    """+79000000000 → «+7 (900) 000-00-00»; незнакомый формат — как есть."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 11 and digits[0] in "78":
        if digits[0] == "8":
            digits = "7" + digits[1:]
        return (
            f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        )
    return phone


def _format_price(price: float) -> str:
    """2500 → «2 500 ₽»."""
    return f"{round(price):,}".replace(",", " ") + " ₽"


class NegotiationScript:
    """Скрипт заключения заказа с оплатой напрямую на карту/СБП."""

    def __init__(
        self,
        policy: PaymentPolicy,
        requisites: PaymentRequisites,
        rng: random.Random | None = None,
    ) -> None:
        self._policy = policy
        self._requisites = requisites
        self._rng = rng or random

    def _pick(self, variants: list[str]) -> str:
        return self._rng.choice(variants)

    def terms_message(self, price: float) -> str:
        """Предложение условий: стоимость + схема оплаты (живым языком)."""
        price_s = _format_price(price)
        advance = self._policy.initial_advance(price)

        if advance >= price:
            return self._pick([
                f"Добрый день! Спасибо, что рассмотрели. Цена — {price_s}. "
                "Условие простое: предоплата 100% — и я сразу приступаю. "
                "Реквизиты для перевода скину.",
                f"Привет! Готов взяться за {price_s}. Работаю по предоплате "
                "(полностью) — переведёте, и в этот же день отдаю результат.",
                f"Здравствуйте! По цене договорились на {price_s}. Из условий "
                "только предоплата 100%, дальше всё быстро — результат "
                "отправлю, как только закончу.",
            ])

        if advance > 0:
            percent = round(self._policy.advance_fraction * 100)
            advance_s = _format_price(advance)
            return self._pick([
                f"Цена — {price_s}. Беру предоплату {advance_s} "
                f"({percent}%), остальное — когда отдам готовый результат. "
                "Так и вам, и мне спокойнее.",
                f"{price_s} за работу. Обычно прошу вперёд {advance_s}, "
                "остаток по готовности.",
                f"Стоимость — {price_s}. Часть ({advance_s}) вперёд, "
                "остаток после сдачи работы.",
            ])

        return self._pick([
            f"Цена — {price_s}. Оплата после того, как отдам результат — "
            "реквизиты отправлю, переведёте по готовности.",
            f"{price_s} за работу. Рассчитаемся по факту: получаете "
            "результат и переводите на реквизиты.",
            f"Стоимость {price_s}, оплата по готовности — сначала работа, "
            "потом перевод.",
        ])

    def requisites_message(self) -> str:
        """Реквизиты для оплаты — естественным текстом."""
        r = self._requisites
        phone = _format_phone(r.sbp_phone) if r.sbp_phone else ""
        card = r.card_masked
        holder = r.holder
        bank = r.bank

        if phone:
            holder_part = f", получатель {holder}" if holder else ""
            bank_part = f", банк {bank}" if bank else ""
            card_part = f". Если удобнее картой — {card}" if card else "."
            return self._pick([
                f"Перевести можно по СБП на номер {phone}{holder_part}"
                f"{bank_part}{card_part}",
                f"Реквизиты: СБП — {phone}{holder_part}{bank_part}"
                f"{card_part}",
                f"Удобно по СБП на {phone}{holder_part}{bank_part}"
                f"{card_part}",
            ])
        if card:
            bank_part = f", банк {bank}" if bank else ""
            return self._pick([
                f"Перевести можно на карту {card}{bank_part}",
                f"Реквизиты: карта {card}{bank_part}",
            ])
        return "Реквизиты для перевода уточню отдельно."

    def handle_safe_deal_objection(self) -> str:
        """Ответ на «давай через безопасную сделку площадки»."""
        if self._policy.insist_on_card():
            return self._pick([
                "Про безопасную сделку — понимаю, но я работаю только с "
                "прямыми переводами: так быстрее и без комиссии площадки. "
                "Реквизиты выше — как переведёте, сразу приступаю.",
                "Спасибо за предложение, но через сделку площадки, к "
                "сожалению, не работаю — только напрямую. Всё прозрачно: "
                "реквизиты отправил, по оплате сразу берусь.",
                "Понимаю. Принимаю оплату только напрямую — надёжнее, без "
                "задержек и комиссий. Как только увижу перевод, начну.",
            ])
        return self._pick([
            "Можно и через безопасную сделку — как вам удобнее. Я обычно "
            "работаю по прямым переводам, но не настаиваю.",
            "Давайте так, как комфортнее вам: могу и через сделку площадки, "
            "могу напрямую. Решайте.",
            "Без проблем, можно и безопасную сделку. Я предпочитаю прямые "
            "переводы — быстрее, но вам как удобнее.",
        ])

