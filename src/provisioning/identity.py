"""Генерация профиля для регистрации (Трек B5).

KYC-примечание: для вывода средств площадки требуют верификацию реальной
личности (docs/SCOPE.md). Здесь — только данные формы, не фиктивная личность
для обхода KYC.
"""
from __future__ import annotations

import random

FIRST_NAMES = [
    "Алексей", "Дмитрий", "Сергей", "Андрей", "Михаил",
    "Игорь", "Павел", "Николай", "Артём", "Владимир",
]
LAST_NAMES = [
    "Иванов", "Петров", "Смирнов", "Кузнецов", "Соколов",
    "Волков", "Морозов", "Фёдоров", "Козлов", "Новиков",
]


class IdentityGenerator:
    """Генерирует согласованный набор данных профиля (имя, дата рождения)."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random

    def generate(self, platform: str) -> dict:
        year = self._rng.randint(1985, 2000)
        return {
            "platform": platform,
            "first_name": self._rng.choice(FIRST_NAMES),
            "last_name": self._rng.choice(LAST_NAMES),
            "birth_date": (
                f"{self._rng.randint(1, 28):02d}."
                f"{self._rng.randint(1, 12):02d}.{year}"
            ),
        }

