"""dry-run провайдеры: эмуляция почты, SMS и капчи без внешних сервисов.

Используются по умолчанию (EMAIL_PROVIDER/SMS_PROVIDER/CAPTCHA_PROVIDER=dry_run),
чтобы весь конвейер регистрации работал и тестировался автономно.
"""
from __future__ import annotations

import random

from src.provisioning.providers.base import CaptchaProvider, EmailProvider, SmsProvider


class DryRunEmailProvider(EmailProvider):
    """Эмуляция почты: ящик генерируется, код подтверждения фиксированный."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random

    async def create_mailbox(self, platform: str) -> dict:
        suffix = self._rng.randint(100000, 999999)
        return {
            "email": f"autofl.{platform}.{suffix}@dry.local",
            "password": "dry-password",
            "provider": "dry_run",
        }

    async def wait_for_code(
        self, mailbox: dict, timeout_seconds: int = 120
    ) -> str | None:
        return "111111"


class DryRunSmsProvider(SmsProvider):
    """Эмуляция SMS-активации: номер генерируется, код фиксированный."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random

    async def request_number(self, platform: str) -> dict:
        suffix = self._rng.randint(1000000, 9999999)
        return {
            "activation_id": f"dry-{platform}-{suffix}",
            "number": f"+79{suffix}",
            "cost": 5.0,
            "service": "dry_run",
        }

    async def wait_for_code(
        self, activation_id: str, timeout_seconds: int = 120
    ) -> str | None:
        return "222222"

    async def cancel(self, activation_id: str) -> None:
        return None


class DryRunCaptchaProvider(CaptchaProvider):
    """Эмуляция решения капчи."""

    async def solve_image(self, image_b64: str) -> str:
        return "dry-captcha"

    async def solve_token(self, site_key: str, page_url: str) -> str:
        return "dry-token"
