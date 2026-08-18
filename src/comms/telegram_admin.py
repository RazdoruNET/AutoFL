"""Админ-бот оператора: сводки, аппрувы, kill switch (Этап 8)."""
from src.config.settings import get_settings


class TelegramAdmin:
    """Обёртка над aiogram для канала оператора."""

    async def notify(self, text: str) -> None:
        """Отправка сообщения в админ-чат (сводки, алерты, запросы)."""
        # Этап 8: aiogram-клиент, очередь аппрувов, kill switch.
        raise NotImplementedError("Этап 8: TelegramAdmin.notify")
