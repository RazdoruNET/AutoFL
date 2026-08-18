"""Клиент 5sim.net (SMS-активация) (Трек B3).

Документация: https://5sim.net/docs/api
Внимание: live-проверка не проводилась (нужен токен) — сверь параметры
с актуальной документацией сервиса после получения токена.
"""
from __future__ import annotations

import asyncio
import re

import httpx

from src.provisioning.providers.base import SmsProvider

_CODE_RE = re.compile(r"\b(\d{4,6})\b")


class FiveSimProvider(SmsProvider):
    BASE_URL = "https://5sim.net/v1"

    def __init__(
        self,
        api_key: str,
        service_map: dict[str, str] | None = None,
        country: str = "russia",
        operator: str = "any",
        timeout: float = 30.0,
        poll_interval: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._service_map = service_map or {}
        self._country = country
        self._operator = operator
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._transport = transport

    def _product(self, platform: str) -> str:
        return self._service_map.get(platform, platform)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self._timeout,
            transport=self._transport,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Accept": "application/json",
            },
        )

    async def request_number(self, platform: str) -> dict:
        url = (
            f"{self.BASE_URL}/user/buy/activation/"
            f"{self._country}/{self._operator}/{self._product(platform)}"
        )
        async with self._client() as client:
            resp = await client.get(url)
            data = resp.json()
        if "id" not in data:
            raise RuntimeError(f"5sim: {data}")
        return {
            "activation_id": str(data["id"]),
            "number": data.get("phone", ""),
            "service": "5sim",
            "cost": float(data.get("price", 0.0)),
        }

    async def wait_for_code(
        self, activation_id: str, timeout_seconds: int = 120
    ) -> str | None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_seconds
        async with self._client() as client:
            while loop.time() < deadline:
                resp = await client.get(f"{self.BASE_URL}/user/check/{activation_id}")
                data = resp.json()
                sms_list = data.get("sms") or []
                if sms_list:
                    last = sms_list[-1]
                    if last.get("code"):
                        return str(last["code"])
                    match = _CODE_RE.search(last.get("text", ""))
                    if match:
                        return match.group(1)
                    return last.get("text", "")[:300] or None
                await asyncio.sleep(self._poll_interval)
        return None

    async def cancel(self, activation_id: str) -> None:
        async with self._client() as client:
            await client.get(f"{self.BASE_URL}/user/cancel/{activation_id}")
