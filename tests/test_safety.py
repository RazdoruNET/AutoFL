"""Детерминированные правила безопасности (Этап 5)."""
import pytest

from src.brain.safety import apply_stop_rules


def test_clean_task_allowed():
    verdict = apply_stop_rules(
        "Нужно переписать текст объявления для сайта, 3000 знаков"
    )
    assert verdict.allowed
    assert verdict.score == 1.0
    assert verdict.reasons == []


@pytest.mark.parametrize(
    "text",
    [
        "Зарегистрируй меня на сайте",
        "Оставь отзыв на маркетплейсе",
        "Нужен паспорт для аккаунта",
        "Переведи деньги на карту",
        "Пройди капчу и подтверди",
        "Накрути подписчиков",
        "Зайди в чужой аккаунт",
    ],
)
def test_stop_rules_reject(text: str):
    verdict = apply_stop_rules(text)
    assert not verdict.allowed
    assert verdict.score == 0.0
    assert verdict.reasons, "должен быть указан задетый паттерн"
