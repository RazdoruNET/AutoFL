# AutoFL — автономный фриланс-агент

**AutoFL** ищет, ведёт и выполняет простые задания на фриланс-площадках:
обнаружение в ленте → безопасная классификация → подготовка результата →
сопровождение заказчика. Автономность включается поэтапно и до финальной
фазы всегда под контролем оператора (human-in-the-loop).

> ⚠️ Площадки запрещают автоматизацию. Система построена так, чтобы
> минимально воздействовать на аккаунт: read-only фазы, вежливые rate-limit'ы,
> ручной вход, гейты одобрения. Использование — на ответственность владельца
> аккаунта. Подробности — в [docs/SCOPE.md](docs/SCOPE.md).

## Возможности

- 🔍 **Поиск заданий** — Playwright-адаптеры площадок (Kwork, FL.ru, YouDo),
  дедупликация по `(platform, external_id)`, вежливый rate-limit.
- 🛡 **Безопасная классификация** — детерминированные стоп-правила до LLM +
  скоринг модели, порог `MIN_SAFETY_SCORE`.
- ⚙️ **Выполнение** — тексты (рерайт/перевод/описания), данные (парсинг/
  таблицы), код — только в изолированной песочнице.
- 🧭 **Машина состояний** — идемпотентные переходы, восстановление после
  краша без двойных отправок; состояния оплаты (Трек B9).
- 💳 **Финансы (Трек B)** — реквизиты карты/СБП (PAN зашифрован), верификация
  прихода оплаты, лимиты расходов, авто-траты на SMS/капчу/почту/подписки.
- 🤝 **Переговоры (Трек B9)** — заключение заказа живым языком: несколько
  формулировок на каждый случай (случайный выбор), без «машинных» маркеров;
  настаивание на оплате напрямую на карту (`card_required`) либо уступка
  сделке площадки.
- 👤 **Human-in-the-loop** — гейты одобрения, kill switch, лимиты
  (`DAILY_BUDGET_RUB`, `MAX_CONCURRENT_TASKS`).
- 📊 **Мониторинг** — админ-бот Telegram, FastAPI `/healthz`, `/status`,
  структурированные логи.

## Статус

| Этап | Статус |
|---|---|
| 0 — скоуп и риски | ✅ done |
| 1 — каркас и конфигурация | ✅ done |
| B1 — карта и платёжная инфраструктура | ✅ done |
| B9 — переговоры и приём оплаты | ✅ done |
| 2–11, B2–B8 | ⏳ pending (см. `progress.json`) |

План разработки — [`MASTER_PLAN.md`](MASTER_PLAN.md).

## Быстрый старт

### 1. Требования

- Python 3.11+ (проверено на 3.14)
- Ollama (по умолчанию) либо ключ OpenAI/Anthropic
- Playwright: `playwright install chromium` (нужно только для адаптеров площадок)

### 2. Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Конфигурация

```bash
cp .env.example .env
```

Ключевые переменные:

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` / `openai` / `anthropic` |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | адрес локального инференса |
| `LLM_MODEL` | `nemotron-3-nano:4b` | модель |
| `PLATFORMS` | — | площадки через запятую: `kwork,flru,youdo` |
| `AUTO_EXECUTE` | `false` | полная автономность (только после Этапа 8) |
| `APPROVAL_REQUIRED` | `true` | внешние действия требуют одобрения |
| `MIN_SAFETY_SCORE` | `0.85` | порог допуска задачи |
| `DRY_RUN` | `true` | ничего не отправлять, только логировать |

### 4. Запуск

```bash
python -m src.main            # инициализация конфигурации и логов
python -m src.db.init_db      # создание схемы БД (временный путь до Alembic)
uvicorn src.api.app:app       # API: http://127.0.0.1:8000/healthz
```

### 5. Тесты

```bash
pytest -v
```

## Структура

```
src/
├── main.py            # точка входа
├── config/settings.py # pydantic-settings (.env)
├── observability.py   # логи (rotating)
├── security/vault.py  # шифрование карт/паролей/сессий (Fernet)
├── db/                # SQLAlchemy-модели, сессии, init_db
├── platforms/         # base adapter + kwork/flru/youdo + auth + registry
├── discovery/         # fetcher + dedupe
├── brain/             # safety (правила) + classifier (LLM) + prompts
├── executor/          # text / data / code (песочница) + quality
├── workflow/          # state_machine (оплата) + approvals + pipeline
├── comms/             # messages + negotiation (оплата на карту) + telegram_admin
├── finance/           # requisites + payment_verification + wallet + budget + spending
├── provisioning/      # email / phone (SMS) / captcha / registrar (Трек B)
├── agent/             # planner + commander (Трек B7)
├── sandbox/           # изолированное выполнение кода
└── api/app.py         # FastAPI: /healthz, /status
```
