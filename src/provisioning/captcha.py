"""Решение капчи: внешний сервис + локальный fallback (Трек B4).

Провайдер выбирается из настроек (PROVISIONING_PROVIDER); по умолчанию —
dry_run. Реальные реализации (RuCaptcha / 2Captcha / anti-captcha)
добавляются в src/provisioning/providers.py по API-ключам.
"""
from __future__ import annotations

from src.provisioning.providers import CaptchaProvider, get_captcha_provider


class CaptchaSolver:
    def __init__(self, provider: CaptchaProvider | None = None) -> None:
        self._provider = provider or get_captcha_provider()

    async def solve_image(self, image_b64: str) -> str:
        """Решает графическую капчу; возвращает текст решения."""
        return await self._provider.solve_image(image_b64)

    async def solve_token(self, site_key: str, page_url: str) -> str:
        """Решает токен-капчу (reCAPTCHA/hCaptcha); возвращает токен."""
        return await self._provider.solve_token(site_key, page_url)

