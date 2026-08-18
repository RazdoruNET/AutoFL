"""FastAPI: мониторинг и управление AutoFL.

Полный набор эндпоинтов (/tasks, /approve, /earnings) — Этап 9.
"""
from fastapi import FastAPI

from src.config.settings import get_settings
from src.observability import get_logger

logger = get_logger("autofl.api")

settings = get_settings()

app = FastAPI(title="AutoFL API", version="0.1.0")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "stage": "skeleton"}


@app.get("/status")
async def status() -> dict:
    return {
        "platforms": settings.platform_list,
        "llm": {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "ready": settings.llm_ready,
        },
        "behavior": {
            "dry_run": settings.dry_run,
            "auto_execute": settings.auto_execute,
            "approval_required": settings.approval_required,
            "min_safety_score": settings.min_safety_score,
        },
    }
