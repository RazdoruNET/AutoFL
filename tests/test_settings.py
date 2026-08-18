"""Конфигурация: чтение и валидация настроек (Этап 1)."""
from src.config.settings import Settings


def test_defaults():
    s = Settings()
    assert s.min_safety_score == 0.85
    assert s.approval_required is True
    assert s.auto_execute is False
    assert s.dry_run is True
    assert s.max_revisions == 2


def test_platform_list_normalized():
    s = Settings(platforms="kwork, flru, YOUDO")
    assert s.platform_list == ["kwork", "flru", "youdo"]


def test_platform_list_empty():
    assert Settings(platforms="").platform_list == []


def test_llm_ready():
    ok = Settings(
        llm_provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        llm_model="nemotron-3-nano:4b",
    )
    assert ok.llm_ready

    no_key = Settings(llm_provider="openai", openai_api_key="", llm_model="gpt-4o-mini")
    assert not no_key.llm_ready

    unknown = Settings(llm_provider="unknown")
    assert not unknown.llm_ready
