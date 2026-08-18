"""Бесплатная temp-почта 1secmail.com (Трек B2).

API: https://www.1secmail.com/api/
Подходит как старт без бюджета. Внимание: temp-почта может не принимать
письма некоторых сервисов и менее надёжна, чем собственный домен.
"""
from __future__ import annotations

import asyncio
import re

import httpx

from src.provisioning.providers.base import EmailProvider

_CODE_RE = re.compile(r"\b(\d{6})\b")


class OneSecMailProvider(EmailProvider):
    API_URL = "https://www.1secmail.com/api/v1/"

    def __init__(
        self,
        timeout: float = 30.0,
        poll_interval: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._transport = transport

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout, transport=self._transport)

    async def create_mailbox(self, platform: str) -> dict:
        async with self._client() as client:
            resp = await client.get(
                self.API_URL, params={"action": "genRandomMailbox", "count": 1}
            )
            resp.raise_for_status()
            email = resp.json()[0]
        login, domain = email.split("@")
        return {
            "email": email,
            "password": "",
            "provider": "1secmail",
            "login": login,
            "domain": domain,
        }

    async def wait_for_code(
        self, mailbox: dict, timeout_seconds: int = 120
    ) -> str | None:
        login = mailbox["login"]
        domain = mailbox["domain"]
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_seconds
        async with self._client() as client:
            while loop.time() < deadline:
                resp = await client.get(
                    self.API_URL,
                    params={"action": "getMessages", "login": login, "domain": domain},
                )
                messages = resp.json()
                if messages:
                    msg = messages[0]
                    full = await client.get(
                        self.API_URL,
                        params={
                            "action": "readMessage",
                            "login": login,
                            "domain": domain,
                            "id": msg["id"],
                        },
                    )
                    body = full.json().get("body", "")
                    match = _CODE_RE.search(body)
                    if match:
                        return match.group(1)
                    return body[:300] or None
                await asyncio.sleep(self._poll_interval)
        return None
