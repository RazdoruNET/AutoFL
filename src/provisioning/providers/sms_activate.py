"""Клиент SMS-активации sms-activate.org (Трек B3).

Документация: https://sms-activate.org/cp/api-docs
Внимание: live-проверка не проводилась (нужен ключ) — сверь параметры
с актуальной документацией сервиса после получения API-ключа.
"""
from __future__ import annotations

import asyncio

import httpx

from src.provisioning.providers.base import SmsProvider


class SmsActivateProvider(SmsProvider):
    BASE_URL = "https://sms-activate.org/stubs/handler_api.php"

    def __init__(
        self,
        api_key: str,
        service_map: dict[str, str] | None = None,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._service_map = service_map or {}
        self._timeout = timeout
        self._transport = transport

    def _service(self, platform: str) -> str:
        return self._service_map.get(platform, platform)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout, transport=self._transport)

    async def request_number(self, platform: str) -> dict:
        params = {
            "api_key": self._api_key,
            "action": "getNumber",
            "service": self._service(platform),
        }
        async with self._client() as client:
            resp = await client.get(self.BASE_URL, params=params)
            text = resp.text.strip()
        if text.startswith("ACCESS_NUMBER"):
            _, activation_id, number = text.split(":")
            return {
                "activation_id": activation_id,
                "number": number,
                "service": "sms_activate",
                "cost": 0.0,
            }
        raise RuntimeError(f"sms-activate: {text}")  # NO_NUMBERS | NO_BALANCE | BAD_KEY

    async def wait_for_code(
        self, activation_id: str, timeout_seconds: int = 120
    ) -> str | None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_seconds
        async with self._client() as client:
            while loop.time() < deadline:
                params = {
                    "api_key": self._api_key,
                    "action": "getStatus",
                    "id": activation_id,
                }
                resp = await client.get(self.BASE_URL, params=params)
                text = resp.text.strip()
                if text.startswith("STATUS_OK"):
                    return text.split(":", 1)[1]
                if text == "STATUS_WAIT_CODE":
                    await asyncio.sleep(3)
                    continue
                raise RuntimeError(f"sms-activate status: {text}")
        return None

    async def cancel(self, activation_id: str) -> None:
        params = {
            "api_key": self._api_key,
            "action": "setStatus",
            "id": activation_id,
            "status": 8,  # отмена активации
        }
        async with self._client() as client:
            await client.get(self.BASE_URL, params=params)
