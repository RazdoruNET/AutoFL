"""Создание почтовых ящиков и чтение кодов подтверждения (Трек B2).

Провайдер выбирается из настроек (PROVISIONING_PROVIDER); по умолчанию —
dry_run. Реальные реализации (собственный домен IMAP/SMTP или temp-mail API)
добавляются в src/provisioning/providers.py.
"""
from __future__ import annotations

from src.provisioning.providers import EmailProvider, get_email_provider


class MailboxManager:
    def __init__(self, provider: EmailProvider | None = None) -> None:
        self._provider = provider or get_email_provider()

    async def create(self, platform: str) -> dict:
        return await self._provider.create_mailbox(platform)

    async def wait_for_code(
        self, mailbox: dict, timeout_seconds: int = 120
    ) -> str | None:
        return await self._provider.wait_for_code(mailbox, timeout_seconds)

