"""Абстракции внешних провайдеров для регистрации (Трек B2-B5).

Реализации: dry_run (эмуляция), sms_activate, 5sim, rucaptcha/2captcha,
1secmail (temp-почта). Выбор — через фабрики в этом пакете.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class EmailProvider(ABC):
    @abstractmethod
    async def create_mailbox(self, platform: str) -> dict: ...

    @abstractmethod
    async def wait_for_code(
        self, mailbox: dict, timeout_seconds: int = 120
    ) -> str | None: ...


class SmsProvider(ABC):
    @abstractmethod
    async def request_number(self, platform: str) -> dict: ...

    @abstractmethod
    async def wait_for_code(
        self, activation_id: str, timeout_seconds: int = 120
    ) -> str | None: ...

    @abstractmethod
    async def cancel(self, activation_id: str) -> None: ...


class CaptchaProvider(ABC):
    @abstractmethod
    async def solve_image(self, image_b64: str) -> str: ...

    @abstractmethod
    async def solve_token(self, site_key: str, page_url: str) -> str: ...
