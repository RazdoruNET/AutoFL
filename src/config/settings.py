"""Конфигурация AutoFL через pydantic-settings (.env).

Все параметры документированы в `.env.example`.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ===================== LLM ============================
    llm_provider: str = Field("ollama", description="ollama | openai | anthropic")
    ollama_base_url: str = Field("http://127.0.0.1:11434")
    llm_model: str = Field("nemotron-3-nano:4b")
    openai_api_key: str = Field("")
    anthropic_api_key: str = Field("")
    llm_timeout_seconds: int = Field(120)
    llm_retries: int = Field(2)
    llm_temperature: float = Field(0.3)

    # ===================== Площадки ========================
    platforms: str = Field("")
    browser_headless: bool = Field(True)
    browser_slow_mo_ms: int = Field(0)
    proxy_url: str = Field("")
    user_agent: str = Field("")
    discover_rate_limit_seconds: int = Field(30)

    # ===================== Поведение ========================
    auto_execute: bool = Field(False)
    approval_required: bool = Field(True)
    min_safety_score: float = Field(0.85)
    max_concurrent_tasks: int = Field(1)
    daily_budget_rub: float = Field(0.0)
    max_revisions: int = Field(2)
    dry_run: bool = Field(True)

    # ===================== Регистрация (Трек B) ==============
    # Провайдеры: dry_run (эмуляция) | 1secmail (почта) |
    # sms_activate | 5sim (SMS) | rucaptcha | 2captcha (капча)
    email_provider: str = Field("dry_run")
    sms_provider: str = Field("dry_run")
    captcha_provider: str = Field("dry_run")
    # Ключи реальных провайдеров (пусто — недоступны)
    sms_activate_api_key: str = Field("")
    five_sim_api_key: str = Field("")
    captcha_api_key: str = Field("")
    # Сервис капчи: rucaptcha | 2captcha
    captcha_service: str = Field("rucaptcha")
    # Карта platform -> код продукта/сервиса для SMS (JSON в .env)
    sms_service_map: dict[str, str] = Field(default_factory=dict)

    # ===================== Финансы и оплата (Трек B) ==========
    # Режим приёма оплаты: card_required | card_preferred
    payment_policy: str = Field("card_required")
    # Схема оплаты: advance | partial_advance | on_delivery
    payment_scheme: str = Field("advance")
    # Верификация прихода: manual | bank_sms
    payment_verification_mode: str = Field("manual")
    # Реквизиты по умолчанию для приёма оплаты (FundingSource при старте)
    default_card_holder: str = Field("")
    default_card_sbp_phone: str = Field("")
    default_card_bank: str = Field("")
    # Авто-трата без подтверждения оператора, руб. (выше — аппрув)
    spending_auto_limit_rub: float = Field(200.0)
    # Ключ шифрования vault (пусто — автогенерация в data/vault.key)
    vault_key: str = Field("")

    # ===================== Telegram (админ) =================
    telegram_bot_token: str = Field("")
    admin_chat_id: str = Field("")

    # ===================== База данных =======================
    db_url: str = Field("sqlite+aiosqlite:///data/autofl.db")

    # ===================== HTTP API ==========================
    api_host: str = Field("127.0.0.1")
    api_port: int = Field(8000)

    # ===================== Логи ==============================
    log_level: str = Field("INFO")

    @property
    def platform_list(self) -> list[str]:
        """Площадки, заданные через запятую в PLATFORMS."""
        return [p.strip().lower() for p in self.platforms.split(",") if p.strip()]

    @property
    def llm_ready(self) -> bool:
        """True, если настроен рабочий провайдер LLM."""
        if self.llm_provider == "ollama":
            return bool(self.ollama_base_url and self.llm_model)
        if self.llm_provider == "openai":
            return bool(self.openai_api_key and self.llm_model)
        if self.llm_provider == "anthropic":
            return bool(self.anthropic_api_key and self.llm_model)
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
