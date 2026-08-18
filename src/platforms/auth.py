"""Авторизация на площадках: ручной вход + сохранение сессии (Этап 3).

Политика: вход выполняет оператор вручную (капча/2FA решаются человеком),
бот сохраняет Playwright storage_state и переиспользует его. Автоматическое
решение капчи не предусмотрено и не планируется.
"""
from pathlib import Path

SESSION_DIR = Path(__file__).resolve().parents[2] / "data" / "sessions"


def ensure_session_dir() -> Path:
    """Создаёт каталог для storage_state и возвращает путь."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_DIR


def session_path(platform_slug: str, account_id: int) -> Path:
    """Путь к файлу storage_state для конкретного аккаунта."""
    return ensure_session_dir() / f"{platform_slug}_{account_id}.json"


def has_valid_session(platform_slug: str, account_id: int) -> bool:
    return session_path(platform_slug, account_id).exists()
