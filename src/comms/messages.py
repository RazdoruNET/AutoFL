"""Переписка с заказчиком (Этап 7).

Ревизии обрабатываются ограниченно (MAX_REVISIONS); при исчерпании —
эскалация оператору, а не бесконечный цикл генерации.
"""
from src.config.settings import get_settings


class ClientComms:
    """Сообщения заказчику и bounded-обработка ревизий."""

    async def send(self, task_id: int, text: str) -> None:
        """Отправка сообщения заказчику через адаптер площадки."""
        raise NotImplementedError("Этап 7: ClientComms.send")

    async def handle_revision(self, task_id: int, client_request: str) -> str:
        """Решение по ревизии: 'rework' | 'deliver' | 'escalate'."""
        # Этап 7: подсчёт использованных ревизий, сравнение с лимитом.
        raise NotImplementedError("Этап 7: ClientComms.handle_revision")
