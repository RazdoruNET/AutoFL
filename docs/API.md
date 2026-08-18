# HTTP API (FastAPI)

Приложение: `src/api/app.py`. Запуск:

```bash
uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

> Сейчас реализованы только эндпоинты мониторинга. Полный набор
> (`/tasks`, `/approve`, `/earnings`) — Этап 9 (`MASTER_PLAN.md`).

## GET /healthz

Статус приложения.

```json
{ "status": "ok", "stage": "skeleton" }
```

## GET /status

Конфигурация и поведение (без секретов).

```json
{
  "platforms": ["kwork", "flru"],
  "llm": { "provider": "ollama", "model": "nemotron-3-nano:4b", "ready": true },
  "behavior": {
    "dry_run": true,
    "auto_execute": false,
    "approval_required": true,
    "min_safety_score": 0.85
  }
}
```

## Запланировано (Этап 9)

| Эндпоинт | Назначение |
|---|---|
| `GET /tasks` | список задач и их статусы |
| `POST /approve` | одобрение/отклонение внешних действий |
| `GET /earnings` | заработок и расходы (ledger) |

## Быстрая проверка

```bash
curl http://127.0.0.1:8000/healthz
curl http://127.0.0.1:8000/status
```
