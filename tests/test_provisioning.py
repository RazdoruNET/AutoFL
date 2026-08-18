"""Конвейер регистрации: dry-run провайдеры, identity, registrar (Трек B5)."""
import random

from src.provisioning.captcha import CaptchaSolver
from src.provisioning.email import MailboxManager
from src.provisioning.identity import IdentityGenerator
from src.provisioning.phone import SmsActivation
from src.provisioning.providers import (
    DryRunCaptchaProvider,
    DryRunEmailProvider,
    DryRunSmsProvider,
)
from src.provisioning.registrar import AccountRegistrar
from src.security.vault import decrypt_text


async def _fake_persist(platform: str, mailbox: dict, phone: dict, creds_enc: str) -> dict:
    return {"account_id": 1, "login": mailbox["email"]}


def test_identity_has_required_keys():
    profile = IdentityGenerator(rng=random.Random(1)).generate("kwork")
    assert {"platform", "first_name", "last_name", "birth_date"} <= set(profile)
    assert profile["platform"] == "kwork"


async def test_registrar_dry_run_full_flow():
    registrar = AccountRegistrar(
        identity=IdentityGenerator(rng=random.Random(1)),
        email=MailboxManager(DryRunEmailProvider()),
        phone=SmsActivation(DryRunSmsProvider()),
        captcha=CaptchaSolver(DryRunCaptchaProvider()),
        persist=_fake_persist,
    )
    result = await registrar.register("kwork")
    assert result["account_id"] == 1
    assert result["login"].endswith("@dry.local")
    assert result["phone"].startswith("+79")
    assert result["platform"] == "kwork"


async def test_registrar_credentials_encrypted():
    seen: dict[str, str] = {}

    async def persist(platform, mailbox, phone, creds_enc):
        seen["creds_enc"] = creds_enc
        return {"account_id": 1, "login": mailbox["email"]}

    registrar = AccountRegistrar(persist=persist)
    await registrar.register("kwork")
    decrypted = decrypt_text(seen["creds_enc"])
    assert "111111" in decrypted  # код подтверждения почты
    assert "222222" in decrypted  # SMS-код
    assert "dry.local" in decrypted


async def test_dry_run_providers_work():
    email = DryRunEmailProvider(rng=random.Random(2))
    mailbox = await email.create_mailbox("kwork")
    assert await email.wait_for_code(mailbox, timeout_seconds=5) == "111111"

    sms = DryRunSmsProvider(rng=random.Random(3))
    activation = await sms.request_number("kwork")
    assert "activation_id" in activation
    assert await sms.wait_for_code(activation["activation_id"]) == "222222"
