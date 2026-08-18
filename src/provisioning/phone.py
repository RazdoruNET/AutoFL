"""SMS-активация: получение одноразового номера и кода (Трек B3).

Провайдер выбирается из настроек (PROVISIONING_PROVIDER); по умолчанию —
dry_run. Реальные реализации (sms-activate / 5sim / onlinesim) добавляются
в src/provisioning/providers.py по API-ключам.
"""
from __future__ import annotations

from src.provisioning.providers import SmsProvider, get_sms_provider


class SmsActivation:
    def __init__(self, provider: SmsProvider | None = None) -> None:
        self._provider = provider or get_sms_provider()

    async def request_number(self, platform: str) -> dict:
        """Запрашивает номер под площадку; возвращает activation_id, number."""
        return await self._provider.request_number(platform)

    async def wait_for_code(
        self, activation_id: str, timeout_seconds: int = 120
    ) -> str | None:
        return await self._provider.wait_for_code(activation_id, timeout_seconds)

    async def report_used(self, activation_id: str) -> None:
        """Отмечает номер использованным/освобождает его."""
        await self._provider.cancel(activation_id)

