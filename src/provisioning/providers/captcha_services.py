"""Клиент сервиса решения капчи (RuCaptcha / 2Captcha) (Трек B4).

Протокол у сервисов общий: in.php (отправка) + res.php (опрос результата).
Документация: https://rucaptcha.com/api-rucaptcha
Внимание: live-проверка не проводилась (нужен ключ).
"""
from __future__ import annotations

import asyncio

import httpx

from src.provisioning.providers.base import CaptchaProvider

_HOSTS = {
    "rucaptcha": "http://rucaptcha.com",
    "2captcha": "https://2captcha.com",
}


class CaptchaServiceProvider(CaptchaProvider):
    def __init__(
        self,
        api_key: str,
        service: str = "rucaptcha",
        timeout: float = 30.0,
        poll_interval: float = 5.0,
        wait_seconds: int = 120,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if service not in _HOSTS:
            raise ValueError(f"Неизвестный сервис капчи: {service}")
        self._key = api_key
        self._base = _HOSTS[service]
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._wait = wait_seconds
        self._transport = transport

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self._timeout, transport=self._transport)

    async def _submit_and_poll(self, form: dict) -> str:
        async with self._client() as client:
            resp = await client.post(f"{self._base}/in.php", data=form)
            text = resp.text.strip()
            if not text.startswith("OK|"):
                raise RuntimeError(f"captcha in.php: {text}")
            captcha_id = text.split("|", 1)[1]

            loop = asyncio.get_running_loop()
            deadline = loop.time() + self._wait
            while loop.time() < deadline:
                res = await client.get(
                    f"{self._base}/res.php",
                    params={"key": self._key, "action": "get", "id": captcha_id},
                )
                rtext = res.text.strip()
                if rtext.startswith("OK|"):
                    return rtext.split("|", 1)[1]
                if rtext == "CAPCHA_NOT_READY":
                    await asyncio.sleep(self._poll_interval)
                    continue
                raise RuntimeError(f"captcha res.php: {rtext}")
        raise TimeoutError("captcha: превышен таймаут ожидания решения")

    async def solve_image(self, image_b64: str) -> str:
        return await self._submit_and_poll(
            {"key": self._key, "method": "base64", "body": image_b64}
        )

    async def solve_token(self, site_key: str, page_url: str) -> str:
        return await self._submit_and_poll(
            {
                "key": self._key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
            }
        )
