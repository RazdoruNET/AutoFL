"""Оркестратор автономной регистрации аккаунта (Трек B5).

Поток: профиль → почта → номер → капча → (форма) → подтверждение → vault.
Провайдеры подставляются через provisioning.providers (по умолчанию dry_run).
Реальная отправка формы (Playwright) добавляется с адаптером площадки.
"""
from __future__ import annotations

import json
from typing import Awaitable, Callable

from src.observability import get_logger
from src.provisioning.captcha import CaptchaSolver
from src.provisioning.email import MailboxManager
from src.provisioning.identity import IdentityGenerator
from src.provisioning.phone import SmsActivation
from src.security.vault import encrypt_text

logger = get_logger("autofl.registrar")

# persist(platform, mailbox, phone, creds_enc) -> dict с account_id/login
PersistFn = Callable[[str, dict, dict, str], Awaitable[dict]]


class AccountRegistrar:
    """Выполняет полный цикл регистрации одного аккаунта."""

    def __init__(
        self,
        identity: IdentityGenerator | None = None,
        email: MailboxManager | None = None,
        phone: SmsActivation | None = None,
        captcha: CaptchaSolver | None = None,
        persist: PersistFn | None = None,
    ) -> None:
        self._identity = identity or IdentityGenerator()
        self._email = email or MailboxManager()
        self._phone = phone or SmsActivation()
        self._captcha = captcha or CaptchaSolver()
        self._persist = persist or self._persist_db

    async def register(self, platform: str) -> dict:
        """Регистрирует один аккаунт; возвращает {account_id, login, ...}."""
        logger.info("Регистрация аккаунта на площадке %s", platform)

        profile = self._identity.generate(platform)

        mailbox = await self._email.create(platform)
        email_code = await self._email.wait_for_code(mailbox, timeout_seconds=60)
        if not email_code:
            raise RuntimeError("Не получен код подтверждения почты")

        phone = await self._phone.request_number(platform)
        sms_code = await self._phone.wait_for_code(
            phone["activation_id"], timeout_seconds=60
        )
        if not sms_code:
            await self._phone.report_used(phone["activation_id"])
            raise RuntimeError("Не получен SMS-код")

        captcha_solution = await self._captcha.solve_image("dry:captcha")

        credentials = {
            "login": mailbox["email"],
            "password": mailbox.get("password", ""),
            "profile": profile,
            "phone": phone.get("number", ""),
            "email_code": email_code,
            "sms_code": sms_code,
            "captcha": captcha_solution,
        }
        creds_enc = encrypt_text(json.dumps(credentials, ensure_ascii=False))

        account = await self._persist(platform, mailbox, phone, creds_enc)
        logger.info("Аккаунт %s создан: %s (id=%s)", platform, account["login"], account["account_id"])
        return {
            **account,
            "platform": platform,
            "profile": profile,
            "phone": phone.get("number", ""),
        }

    async def _persist_db(self, platform: str, mailbox: dict, phone: dict, creds_enc: str) -> dict:
        """Сохраняет аккаунт и связанные сущности в БД."""
        from sqlalchemy import select

        from src.db.models import (
            Account,
            Mailbox,
            PhoneNumber,
            Platform,
            ProvisioningJob,
        )
        from src.db.session import get_session

        async with get_session() as session:
            platform_row = await session.scalar(
                select(Platform).where(Platform.slug == platform)
            )
            if platform_row is None:
                platform_row = Platform(slug=platform, name=platform)
                session.add(platform_row)
                await session.flush()

            mb = Mailbox(
                email=mailbox["email"],
                password_enc=encrypt_text(mailbox.get("password", "")),
                provider=mailbox.get("provider", "dry_run"),
                status="used",
            )
            session.add(mb)
            await session.flush()

            pn = PhoneNumber(
                service=phone.get("service", "dry_run"),
                number=phone.get("number", ""),
                status="used",
                cost=phone.get("cost", 0.0),
            )
            session.add(pn)
            await session.flush()

            account = Account(
                platform_id=platform_row.id,
                login=mailbox["email"],
                status="active",
            )
            session.add(account)
            await session.flush()

            job = ProvisioningJob(
                platform_id=platform_row.id,
                email_id=mb.id,
                phone_id=pn.id,
                account_id=account.id,
                status="done",
                credentials_enc=creds_enc,
            )
            session.add(job)
            await session.commit()

            return {"account_id": account.id, "login": account.login}

