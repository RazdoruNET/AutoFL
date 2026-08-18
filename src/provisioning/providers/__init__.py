"""Провайдеры для регистрации: почта, SMS, капча (Трек B2-B5).

Фабрики выбирают реализацию по настройкам:
  EMAIL_PROVIDER   : dry_run | 1secmail
  SMS_PROVIDER     : dry_run | sms_activate | 5sim
  CAPTCHA_PROVIDER : dry_run | rucaptcha | 2captcha

По умолчанию всё в режиме dry_run — конвейер работает без внешних сервисов.
"""
from __future__ import annotations

from src.config.settings import get_settings
from src.provisioning.providers.base import (
    CaptchaProvider,
    EmailProvider,
    SmsProvider,
)
from src.provisioning.providers.captcha_services import CaptchaServiceProvider
from src.provisioning.providers.dry_run import (
    DryRunCaptchaProvider,
    DryRunEmailProvider,
    DryRunSmsProvider,
)
from src.provisioning.providers.five_sim import FiveSimProvider
from src.provisioning.providers.one_sec_mail import OneSecMailProvider
from src.provisioning.providers.sms_activate import SmsActivateProvider

__all__ = [
    "EmailProvider",
    "SmsProvider",
    "CaptchaProvider",
    "DryRunEmailProvider",
    "DryRunSmsProvider",
    "DryRunCaptchaProvider",
    "SmsActivateProvider",
    "FiveSimProvider",
    "CaptchaServiceProvider",
    "OneSecMailProvider",
    "get_email_provider",
    "get_sms_provider",
    "get_captcha_provider",
]


def get_email_provider() -> EmailProvider:
    settings = get_settings()
    mode = settings.email_provider
    if mode == "dry_run":
        return DryRunEmailProvider()
    if mode in {"1secmail", "temp_mail"}:
        return OneSecMailProvider()
    raise ValueError(f"Провайдер почты {mode!r} не реализован")


def get_sms_provider() -> SmsProvider:
    settings = get_settings()
    mode = settings.sms_provider
    if mode == "dry_run":
        return DryRunSmsProvider()
    if mode == "sms_activate":
        if not settings.sms_activate_api_key:
            raise ValueError("SMS_ACTIVATE_API_KEY не задан")
        return SmsActivateProvider(
            settings.sms_activate_api_key, settings.sms_service_map
        )
    if mode in {"5sim", "five_sim"}:
        if not settings.five_sim_api_key:
            raise ValueError("FIVE_SIM_API_KEY не задан")
        return FiveSimProvider(
            settings.five_sim_api_key, settings.sms_service_map
        )
    raise ValueError(f"Провайдер SMS {mode!r} не реализован")


def get_captcha_provider() -> CaptchaProvider:
    settings = get_settings()
    mode = settings.captcha_provider
    if mode == "dry_run":
        return DryRunCaptchaProvider()
    if mode in {"rucaptcha", "2captcha"}:
        if not settings.captcha_api_key:
            raise ValueError("CAPTCHA_API_KEY не задан")
        return CaptchaServiceProvider(
            settings.captcha_api_key, service=settings.captcha_service
        )
    raise ValueError(f"Провайдер капчи {mode!r} не реализован")
