# AutoFL — автономный фриланс-агент

**AutoFL** ищет, ведёт и выполняет простые задания на фриланс-площадках и
**сам создаёт аккаунты фрилансеров по команде оператора**: профиль → почта →
SMS-номер → капча → подтверждение → зашифрованное хранилище учётных данных.
Система распоряжается средствами (карта/СБП) как ресурсом: тратит на
SMS-активацию/капчу/почту и принимает оплату заказов напрямую на карту.

Автономность включается поэтапно и до финальной фазы всегда под контролем
оператора (human-in-the-loop).

> ⚠️ Площадки запрещают автоматизацию и авторегистрацию. Система построена так,
> чтобы минимально воздействовать на аккаунт: dry-run режимы, вежливые
> rate-limit'ы, гейты одобрения, лимиты. Использование — на ответственность
> владельца аккаунта. Подробности, риски и стоп-лист —
> в [docs/SCOPE.md](docs/SCOPE.md).

## Возможности

- 🔍 **Поиск заданий** — Playwright-адаптеры площадок (Kwork, FL.ru, YouDo),
  дедупликация по `(platform, external_id)`, вежливый rate-limit.
- 🛡 **Безопасная классификация** — детерминированные стоп-правила до LLM +
  скоринг модели, порог `MIN_SAFETY_SCORE`.
- ⚙️ **Выполнение** — тексты (рерайт/перевод/описания), данные (парсинг/таблицы),
  код — только в изолированной песочнице.
- 🧭 **Машина состояний** — идемпотентные переходы, восстановление после краха
  без двойных отправок; состояния оплаты (Трек B9).
- 🆕 **Регистрация аккаунтов (Трек B)** — команда оператора «заведи N аккаунтов
  на kwork» → полный конвейер: почта → SMS → капча → подтверждение → vault.
  Провайдеры: dry-run (по умолчанию), готовы клиенты **sms-activate / 5sim /
  RuCaptcha / 2Captcha / 1secmail** — нужно лишь вписать ключи в `.env`.
- 💳 **Финансы (Трек B)** — реквизиты карты/СБП (PAN зашифрован), верификация
  прихода оплаты, лимиты расходов, авто-траты на SMS/капчу/почту/подписки.
- 🤝 **Переговоры (Трек B9)** — заключение заказа живым языком: несколько
  формулировок на каждый случай (случайный выбор), без «машинных» маркеров;
  настаивание на оплате напрямую на карту (`card_required`) либо уступка
  сделке площадки.
- 🔐 **Vault** — Fernet-шифрование карт, паролей, кодов и сессий.
- 👤 **Human-in-the-loop** — гейты одобрения, kill switch, лимиты
  (`DAILY_BUDGET_RUB`, `MAX_CONCURRENT_TASKS`, `SPENDING_AUTO_LIMIT_RUB`).
- 📊 **Мониторинг** — админ-бот Telegram, FastAPI `/healthz`, `/status`,
  структурированные логи (rotating).

## Статус (актуальный — `progress.json`)

| Этап | Статус |
|---|---|
| 0 — скоуп и риски · 1 — каркас и конфигурация | ✅ done |
| B1 — карта и платёжная инфраструктура | ✅ done |
| B2 — почта (dry-run + 1secmail) | ✅ done |
| B3 — SMS-активация (dry-run + sms-activate/5sim) | ✅ done |
| B4 — капча (dry-run + RuCaptcha/2Captcha) | ✅ done |
| B5 — оркестратор регистрации | ✅ done |
| B7 — агент-планировщик (команды оператора) | ✅ done |
| B9 — переговоры и приём оплаты | ✅ done |
| A2–A11, B6, B8 | ⏳ pending |

План разработки — [`MASTER_PLAN.md`](MASTER_PLAN.md). Прогресс — `progress.json`.

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

Полное описание — в [docs/SETUP.md](docs/SETUP.md).

### 4. Запуск

```bash
python -m src.main            # запуск: конфигурация + логи
python -m src.db.init_db      # создать схему БД (data/autofl.db)
uvicorn src.api.app:app       # HTTP API: http://127.0.0.1:8000/healthz
python demo_register.py       # демо регистрации: «заведи 2 аккаунта на kwork»
```

### 5. Тесты

```bash
pytest -v                     # 58 тестов
```

## Команды оператора (Трек B7)

```
заведи 3 аккаунта на kwork
заведите 2 аккаунта для flru
```

`AgentPlanner.plan()` разбирает команду (площадки: `kwork`, `flru`, `youdo`),
`execute()` запускает регистрации. По умолчанию — **dry-run** (эмуляция почты/
SMS/капчи). Режим и ключи — раздел «Регистрация» в конфигурации ниже.

## Конфигурация (ключевые переменные `.env`)

### LLM

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | `ollama` / `openai` / `anthropic` |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | адрес локального инференса |
| `LLM_MODEL` | `nemotron-3-nano:4b` | модель |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | — | ключи внешних провайдеров |

### Площадки и поведение

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `PLATFORMS` | — | площадки через запятую: `kwork,flru,youdo` |
| `PROXY_URL` | — | прокси (для площадок — резидентные) |
| `DISCOVER_RATE_LIMIT_SECONDS` | `30` | пауза между запросами к ленте |
| `AUTO_EXECUTE` | `false` | полная автономность (только после Этапа 8) |
| `APPROVAL_REQUIRED` | `true` | внешние действия требуют одобрения |
| `MIN_SAFETY_SCORE` | `0.85` | порог допуска задачи |
| `DRY_RUN` | `true` | ничего не отправлять, только логировать |
| `MAX_CONCURRENT_TASKS` | `1` | параллельных задач |
| `DAILY_BUDGET_RUB` | `0` | дневной лимит расходов, руб. |
| `MAX_REVISIONS` | `2` | максимум итераций ревизий |

### Регистрация (Трек B)

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `EMAIL_PROVIDER` | `dry_run` | `dry_run` / `1secmail` (бесплатная temp-почта) |
| `SMS_PROVIDER` | `dry_run` | `dry_run` / `sms_activate` / `5sim` |
| `CAPTCHA_PROVIDER` | `dry_run` | `dry_run` / `rucaptcha` / `2captcha` |
| `SMS_ACTIVATE_API_KEY` | — | ключ sms-activate |
| `FIVE_SIM_API_KEY` | — | токен 5sim |
| `CAPTCHA_API_KEY` | — | ключ капча-сервиса |
| `CAPTCHA_SERVICE` | `rucaptcha` | `rucaptcha` / `2captcha` |
| `SMS_SERVICE_MAP` | `{}` | JSON: `{"kwork": "kwork", ...}` |

### Финансы и оплата (Трек B)

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `PAYMENT_POLICY` | `card_required` | настаивать на карту / уступать сделке площадки |
| `PAYMENT_SCHEME` | `advance` | `advance` / `partial_advance` / `on_delivery` |
| `PAYMENT_VERIFICATION_MODE` | `manual` | `manual` / `bank_sms` |
| `DEFAULT_CARD_HOLDER` / `SBP_PHONE` / `BANK` | — | реквизиты для приёма оплаты |
| `SPENDING_AUTO_LIMIT_RUB` | `200` | авто-трата без аппрува, руб. |
| `VAULT_KEY` | — | ключ шифрования (пусто — автогенерация в `data/vault.key`) |

Полный список — в [.env.example](.env.example) и [docs/SETUP.md](docs/SETUP.md).

## Документация

| Документ | Содержание |
|---|---|
| [MASTER_PLAN.md](MASTER_PLAN.md) | план разработки: трек A (поиск/выполнение) и трек B (регистрация/финансы) |
| [docs/SCOPE.md](docs/SCOPE.md) | скоуп, таксономия заданий, стоп-лист, матрица рисков, платёжная модель |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | архитектура, потоки данных, машина состояний, модули |
| [docs/SETUP.md](docs/SETUP.md) | установка, `.env`, подключение провайдеров, запуск |
| [docs/COMMANDS.md](docs/COMMANDS.md) | язык команд оператора и конвейер регистрации |
| [docs/API.md](docs/API.md) | HTTP API (FastAPI) |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | эксплуатация: БД, vault, провайдеры, устранение проблем |

## Структура

```
AutoFL/
├── MASTER_PLAN.md          # план разработки
├── demo_register.py        # демо: регистрация аккаунтов (dry-run)
├── requirements.txt        # зависимости
├── pyproject.toml          # конфиг pytest
├── .env.example            # шаблон конфигурации
├── docs/                   # документация
├── tests/                  # 58 тестов
└── src/
    ├── main.py             # точка входа
    ├── config/settings.py  # pydantic-settings (.env)
    ├── observability.py    # логи (rotating)
    ├── security/vault.py   # Fernet-шифрование карт/паролей/сессий
    ├── db/                 # SQLAlchemy-модели, сессии, init_db
    ├── platforms/          # base adapter + kwork/flru/youdo + auth + registry
    ├── discovery/          # fetcher + dedupe
    ├── brain/              # safety (правила) + classifier (LLM) + prompts
    ├── executor/           # text / data / code (песочница) + quality
    ├── workflow/           # state_machine (оплата) + approvals + pipeline
    ├── comms/              # negotiation (оплата на карту) + payment_policy + admin
    ├── finance/            # requisites + payment_verification + wallet + budget
    ├── provisioning/       # identity/email/phone/captcha/registrar + providers/
    │   └── providers/      # dry_run + sms_activate + five_sim + captcha_services
    ├── agent/              # planner (команды) + commander
    ├── sandbox/            # изолированное выполнение кода
    └── api/app.py          # FastAPI: /healthz, /status
```

