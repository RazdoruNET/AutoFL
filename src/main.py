"""Точка входа AutoFL.

Запуск:  python -m src.main

На этой стадии — инициализация конфигурации и логов.
Полный цикл (поиск → классификация → выполнение → отправка) включается
поэтапно: см. MASTER_PLAN.md и docs/SCOPE.md (фазы A–D).
"""
from src.config.settings import get_settings
from src.observability import get_logger, setup_logging

logger = get_logger("autofl.main")


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("AutoFL v0.1.0 — автономный фриланс-агент")
    logger.info("Площадки: %s", settings.platform_list or "не настроены")
    logger.info("LLM: provider=%s model=%s ready=%s",
                settings.llm_provider, settings.llm_model, settings.llm_ready)
    logger.info("Поведение: dry_run=%s auto_execute=%s approval_required=%s",
                settings.dry_run, settings.auto_execute, settings.approval_required)
    logger.info("API: http://%s:%s  (полная реализация — Этап 9)",
                settings.api_host, settings.api_port)
    logger.warning(
        "Автономное выполнение отключено до завершения Этапа 8 "
        "(human-in-the-loop и лимиты). Сейчас активны только Этапы 0–1 (каркас)."
    )


if __name__ == "__main__":
    main()
