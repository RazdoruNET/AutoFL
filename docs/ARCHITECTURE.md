# Архитектура AutoFL

> Соответствует коду на текущий момент. Этапы разработки — в `MASTER_PLAN.md`,
> скоуп и риски — в `SCOPE.md`.

## 1. Два трека

- **Трек A — поиск и выполнение заданий**: `discover → classify → execute →
  submit → сопровождение заказчика`.
- **Трек B — аккаунты и финансы**: автономная регистрация аккаунтов
  (почта → SMS → капча → форма), реквизиты карты/СБП, верификация прихода
  оплаты, лимиты расходов, переговоры при заключении заказа.

Треки независимы по модулям и связаны через `workflow` (машина состояний
задачи) и `db` (общие таблицы).

## 2. Схема модулей

```
agent/          commander → planner: команда «заведи N аккаунтов на X»
  │
  ▼
provisioning/   identity → email → phone (SMS) → captcha
  │             → registrar (оркестратор) → vault (шифрование)
  ▼
finance/        requisites (карта/СБП) · payment_verification · wallet ·
                budget · spending (авто-траты)
  │
  ▼
comms/          negotiation (живые формулировки, политика card_required/
                card_preferred) · messages · telegram_admin

--- Трек A ---
discovery/      fetcher → dedupe → Candidate
brain/          safety (правила до LLM) → classifier (LLM) → verdict
executor/       text · data · code (sandbox) → quality → Deliverable
platforms/      base adapter → kwork/flru/youdo (Playwright, без API)
workflow/       state_machine · approvals · pipeline

--- Общее ---
config/settings.py   pydantic-settings (.env)
db/                  SQLAlchemy (async), init_db
security/vault.py    Fernet-шифрование
observability.py     логи (rotating)
api/app.py           FastAPI: /healthz, /status
```

## 3. Конвейер регистрации аккаунта (Трек B)

```
команда «заведи 2 аккаунта на kwork»
  → AgentPlanner.plan()    # разбор, валидация площадки/количества
  → AgentPlanner.execute() # для каждого задания:
      AccountRegistrar.register(platform):
        1. IdentityGenerator.generate()    — профиль (имя, дата рождения)
        2. MailboxManager.create()         — почта (dry_run | 1secmail)
           wait_for_code()                 — код подтверждения
        3. SmsActivation.request_number()  — номер (dry_run | sms_activate | 5sim)
           wait_for_code()                 — SMS-код
        4. CaptchaSolver.solve_image()     — капча (dry_run | rucaptcha | 2captcha)
        5. (реальная отправка формы — при интеграции с площадкой, Playwright)
        6. vault.encrypt_text()            — шифрование учётных данных
        7. _persist_db()                   — Account, Mailbox, PhoneNumber,
                                             ProvisioningJob в БД
```

Провайдеры подставляются фабриками `src/provisioning/providers/__init__.py`
по настройкам `EMAIL_PROVIDER` / `SMS_PROVIDER` / `CAPTCHA_PROVIDER`.

## 4. Машина состояний задачи

`src/workflow/state_machine.py` — `TaskStatus` + `ALLOWED_TRANSITIONS`,
функции `can_transition()` / `apply_transition()` (идемпотентны для
терминальных состояний).

```
discovered → classified → rejected | queued → approved → applied
  applied → negotiating → awaiting_payment → paid → executing   (предоплата)
  applied → executing                                          (on_delivery/без оплаты)
  executing → quality_check → ready → submitted
  submitted → delivered | revision_requested | awaiting_payment (on_delivery)
  delivered → done | awaiting_payment
  done → paid
terminal: rejected, cancelled
```

## 5. Провайдеры (src/provisioning/providers/)

| Модуль | Режимы | Статус |
|---|---|---|
| `base.py` | ABC: EmailProvider, SmsProvider, CaptchaProvider | ✅ |
| `dry_run.py` | эмуляция почты/SMS/капчи | ✅ (по умолчанию) |
| `sms_activate.py` | sms-activate.org (getNumber/getStatus/setStatus) | ✅ код готов, live не проверен |
| `five_sim.py` | 5sim.net (buy/check/cancel, Bearer-токен) | ✅ код готов, live не проверен |
| `captcha_services.py` | RuCaptcha/2Captcha (in.php/res.php) | ✅ код готов, live не проверен |
| `one_sec_mail.py` | 1secmail.com (бесплатная temp-почта) | ✅ код готов, live не проверен |

Все клиенты принимают `httpx.MockTransport` для тестов
(`tests/test_provider_clients.py`).

## 6. Финансы и переговоры (Трек B)

- `finance/requisites.py` — сборка реквизитов (СБП-номер предпочтительно;
  PAN — только зашифрован в `FundingSource.pan_enc`).
- `finance/payment_verification.py` — приход: `manual` (оператор) / `bank_sms`
  (сверка суммы).
- `finance/wallet.py` — ledger доходов/расходов; `budget.py` — лимиты категорий;
  `spending.py` — авто-траты до `SPENDING_AUTO_LIMIT_RUB`, выше — аппрув.
- `comms/payment_policy.py` — режимы `card_required` / `card_preferred`, схемы
  `advance` / `partial_advance` / `on_delivery`.
- `comms/negotiation.py` — живой текст: варианты фраз на каждый случай,
  случайный выбор (`rng`), человечный формат телефона и цены.

## 7. Безопасность и лимиты

- `security/vault.py` — Fernet; ключ из `VAULT_KEY` или автогенерация в
  `data/vault.key` (gitignored).
- `brain/safety.py` — стоп-правила **до** LLM (стоп-лист — в `SCOPE.md`).
- `workflow/approvals.py` — гейты одобрения внешних действий.
- Лимиты: `DRY_RUN`, `APPROVAL_REQUIRED`, `AUTO_EXECUTE`, `MIN_SAFETY_SCORE`,
  `DAILY_BUDGET_RUB`, `MAX_CONCURRENT_TASKS`, `SPENDING_AUTO_LIMIT_RUB`.
- Полный PAN и коды никогда не попадают в логи.

## 8. Хранилище (SQLite, async SQLAlchemy)

Таблицы: `platforms`, `accounts`, `sessions`, `candidates`, `tasks`,
`submissions`, `revisions`, `earnings`, `audit_log`, `funding_sources`,
`transactions`, `mailboxes`, `phone_numbers`, `captcha_requests`,
`provisioning_jobs`. Миграции — Alembic (запланировано, Этап 2); сейчас
схема создаётся `python -m src.db.init_db`.

## 9. Реализовано / запланировано

| Подсистема | Состояние |
|---|---|
| Конфигурация, логи, vault, БД-слой | ✅ работает |
| Регистрация: конвейер + dry-run/реальные клиенты | ✅ работает (dry-run) |
| Переговоры и приём оплаты | ✅ работает |
| Машина состояний | ✅ работает |
| Поиск/классификация/выполнение (Трек A) | 🕓 каркас, реализации — этапы 3–7 |
| Адаптеры площадок (Playwright) | 🕓 заглушки, этап 3 |
| Telegram-админ, FastAPI `/tasks` `/approve` | 🕓 этап 8–9 |

