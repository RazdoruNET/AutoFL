# Установка и настройка AutoFL

## 1. Требования

- Python 3.11+ (проверено на 3.14)
- Ollama на `OLLAMA_BASE_URL` (по умолчанию `http://127.0.0.1:11434`) с моделью
  `LLM_MODEL`, либо ключи OpenAI/Anthropic
- Playwright (только для адаптеров площадок, Трек A): `playwright install chromium`

## 2. Установка

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Конфигурация

```bash
cp .env.example .env
```

Все параметры описаны комментариями в `.env.example`. Ключевые группы:

- **LLM** — `LLM_PROVIDER`, `OLLAMA_BASE_URL`, `LLM_MODEL`.
- **Площадки** — `PLATFORMS` (через запятую: `kwork,flru,youdo`).
- **Поведение** — `DRY_RUN`, `AUTO_EXECUTE`, `APPROVAL_REQUIRED`,
  `MIN_SAFETY_SCORE`, `DAILY_BUDGET_RUB`, `MAX_CONCURRENT_TASKS`.
- **Регистрация** — `EMAIL_PROVIDER`, `SMS_PROVIDER`, `CAPTCHA_PROVIDER`,
  API-ключи (`SMS_ACTIVATE_API_KEY`, `FIVE_SIM_API_KEY`, `CAPTCHA_API_KEY`),
  `CAPTCHA_SERVICE`, `SMS_SERVICE_MAP`.
- **Финансы** — `PAYMENT_POLICY`, `PAYMENT_SCHEME`, `PAYMENT_VERIFICATION_MODE`,
  реквизиты `DEFAULT_CARD_*`, `SPENDING_AUTO_LIMIT_RUB`, `VAULT_KEY`.

## 4. Инициализация БД

```bash
python -m src.db.init_db
```

Создаёт `data/autofl.db` (по умолчанию) со всеми таблицами. Каталог `data/`
исключён из git. Alembic-миграции появятся на Этапе 2; пока схема — `create_all`.

## 5. Запуск

```bash
python -m src.main            # конфигурация + логи (быстрая проверка окружения)
uvicorn src.api.app:app       # HTTP API: http://127.0.0.1:8000/healthz
python demo_register.py       # демо регистрации (dry-run) — создаёт аккаунты в БД
```

## 6. Подключение реальных провайдеров (регистрация, Трек B)

### 6.1 Почта

- `EMAIL_PROVIDER=1secmail` — бесплатно, ключ не нужен (temp-почта).
- Позже (надёжнее): собственный домен — реализация IMAP/SMTP-провайдера.

### 6.2 SMS-активация

- `sms-activate.org`: пополнить баланс (~100–200 ₽), получить ключ →
  `SMS_PROVIDER=sms_activate`, `SMS_ACTIVATE_API_KEY=...`.
- `5sim.net`: токен → `SMS_PROVIDER=5sim`, `FIVE_SIM_API_KEY=...`.
- Коды сервисов/продуктов площадок — в `SMS_SERVICE_MAP` (JSON), например:
  ```env
  SMS_SERVICE_MAP={"kwork": "kwork", "flru": "fl", "youdo": "youdo"}
  ```
  Точные коды сверь с документацией сервиса (живой проверки пока не было).

### 6.3 Капча

- `rucaptcha.com` или `2captcha.com`: пополнить (~50–100 ₽), получить ключ →
  `CAPTCHA_PROVIDER=rucaptcha`, `CAPTCHA_API_KEY=...`, `CAPTCHA_SERVICE=rucaptcha`.

### 6.4 Live-проверка

Реальные клиенты написаны по документации, но не проверены без ключей.
После получения ключей прогнать:

```bash
python - <<'PY'
import asyncio
from src.provisioning.providers import get_sms_provider, get_captcha_provider

async def main():
    sms = get_sms_provider()
    print("SMS:", await sms.request_number("kwork"))

asyncio.run(main())
PY
```

## 7. Тесты

```bash
pytest -v
```

58 тестов: конфиг, безопасность, дедупликация, машина состояний, финансы,
переговоры, vault, конвейер регистрации, планировщик, клиенты провайдеров
(на мок-транспорте).

## 8. Устранение неполадок

| Симптом | Причина / решение |
|---|---|
| `NO_BALANCE` (sms-activate) | пополнить баланс сервиса |
| `NO_NUMBERS` | нет номеров под площадку/сервис — сменить `SMS_SERVICE_MAP` или провайдера |
| `BAD_KEY` / `401` | неверный API-ключ |
| БД не создана | `python -m src.db.init_db` (каталог `data/` создаётся автоматически) |
| `VAULT_KEY` сменился | старые зашифрованные данные не расшифруются — храните ключ |
