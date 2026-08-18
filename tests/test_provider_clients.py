"""Клиенты реальных провайдеров: форматы запросов на мок-транспорте.

Live-проверка невозможна без ключей — тесты фиксируют ожидаемый формат
запросов и парсинг ответов по документации сервисов.
"""
import httpx

from src.provisioning.providers.captcha_services import CaptchaServiceProvider
from src.provisioning.providers.five_sim import FiveSimProvider
from src.provisioning.providers.one_sec_mail import OneSecMailProvider
from src.provisioning.providers.sms_activate import SmsActivateProvider


async def test_sms_activate_request_number():
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        return httpx.Response(200, text="ACCESS_NUMBER:777:+79991112233")

    provider = SmsActivateProvider(
        api_key="secret",
        service_map={"kwork": "kwork"},
        transport=httpx.MockTransport(handler),
    )
    result = await provider.request_number("kwork")
    assert result["activation_id"] == "777"
    assert result["number"] == "+79991112233"
    assert "api_key=secret" in seen["url"]
    assert "action=getNumber" in seen["url"]


async def test_sms_activate_wait_for_code():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="STATUS_OK:123456")

    provider = SmsActivateProvider(
        api_key="k", transport=httpx.MockTransport(handler)
    )
    code = await provider.wait_for_code("777", timeout_seconds=10)
    assert code == "123456"


async def test_sms_activate_no_balance_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="NO_BALANCE")

    provider = SmsActivateProvider(
        api_key="k", transport=httpx.MockTransport(handler)
    )
    try:
        await provider.request_number("kwork")
        raise AssertionError("ожидалась ошибка NO_BALANCE")
    except RuntimeError as exc:
        assert "NO_BALANCE" in str(exc)


async def test_five_sim_request_number():
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("Authorization", "")
        return httpx.Response(
            200, json={"id": 9, "phone": "+79998887766", "price": 12.5}
        )

    provider = FiveSimProvider(
        api_key="token",
        service_map={"kwork": "kwork"},
        transport=httpx.MockTransport(handler),
    )
    result = await provider.request_number("kwork")
    assert result["activation_id"] == "9"
    assert result["number"] == "+79998887766"
    assert result["cost"] == 12.5
    assert seen["auth"] == "Bearer token"


async def test_five_sim_wait_for_code():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json={"status": 1, "sms": []})
        return httpx.Response(
            200, json={"status": 1, "sms": [{"text": "Kod: 123456"}]}
        )

    provider = FiveSimProvider(
        api_key="token", poll_interval=0.01, transport=httpx.MockTransport(handler)
    )
    code = await provider.wait_for_code("9", timeout_seconds=10)
    assert code == "123456"


async def test_captcha_solve_image():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("in.php"):
            return httpx.Response(200, text="OK|42")
        return httpx.Response(200, text="OK|qwerty")

    provider = CaptchaServiceProvider(
        api_key="k", service="rucaptcha", poll_interval=0.01,
        transport=httpx.MockTransport(handler),
    )
    assert await provider.solve_image("base64...") == "qwerty"


async def test_captcha_not_ready_then_solved():
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("in.php"):
            return httpx.Response(200, text="OK|42")
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, text="CAPCHA_NOT_READY")
        return httpx.Response(200, text="OK|token123")

    provider = CaptchaServiceProvider(
        api_key="k", service="2captcha", poll_interval=0.01,
        transport=httpx.MockTransport(handler),
    )
    assert await provider.solve_token("sitekey", "https://page/url") == "token123"


async def test_one_sec_mail_create_and_wait_code():
    def handler(request: httpx.Request) -> httpx.Response:
        action = request.url.params.get("action")
        if action == "genRandomMailbox":
            return httpx.Response(200, json=["user@1secmail.com"])
        if action == "getMessages":
            return httpx.Response(200, json=[{"id": 5}])
        if action == "readMessage":
            return httpx.Response(200, json={"body": "Ваш код: 987654"})
        return httpx.Response(200, json=[])

    provider = OneSecMailProvider(
        poll_interval=0.01, transport=httpx.MockTransport(handler)
    )
    mailbox = await provider.create_mailbox("kwork")
    assert mailbox["email"] == "user@1secmail.com"
    assert mailbox["login"] == "user"
    code = await provider.wait_for_code(mailbox, timeout_seconds=10)
    assert code == "987654"
