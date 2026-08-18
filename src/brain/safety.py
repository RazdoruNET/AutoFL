"""Детерминированные правила безопасности (Этап 5).

Срабатывают ДО LLM-классификатора: если задание подпадает под стоп-правило,
оно отклоняется без участия модели.
"""
import re
from dataclasses import dataclass, field


@dataclass
class SafetyVerdict:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    score: float = 1.0


# Стоп-паттерны: скам, нарушения ToS, персональные/платёжные данные.
# Полный реестр запрещённого — в docs/SCOPE.md.
STOP_PATTERNS: list[str] = [
    r"зарегистрир",
    r"остав\w* отзыв",
    r"накрут",
    r"паспорт",
    r"номер\s*карт",
    r"cvv",
    r"смс\s*код",
    r"подтверд\w* личност",
    r"перевед\w* (деньги|денег|оплат)",
    r"перевод\w* (деньги|денег|оплат)",
    r"крипто",
    r"перейди по ссылке",
    r"капч",
    r"голосован",
    r"чуж\w* аккаунт",
    r"взлом",
    r"войти в чуж",
    r"обход защит",
]


def apply_stop_rules(text: str) -> SafetyVerdict:
    """Проверка текста задания по детерминированным правилам.

    Возвращает вердикт: allowed=False + список задетых правил, либо
    allowed=True со скором 1.0, если правила не сработали.
    """
    low = text.lower()
    hits = [p for p in STOP_PATTERNS if re.search(p, low)]
    if hits:
        return SafetyVerdict(allowed=False, reasons=hits, score=0.0)
    return SafetyVerdict(allowed=True)
