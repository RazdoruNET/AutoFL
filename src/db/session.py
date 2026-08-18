"""Фабрика асинхронных сессий SQLAlchemy для AutoFL."""
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config.settings import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _ensure_db_dir(db_url: str) -> None:
    """Для sqlite создаёт каталог файла БД, если его ещё нет."""
    if not db_url.startswith("sqlite"):
        return
    path_part = db_url.split("///", 1)[-1]
    if path_part and not path_part.startswith(":memory:"):
        Path(path_part).expanduser().resolve().parent.mkdir(
            parents=True, exist_ok=True
        )


def init_db() -> None:
    """Создаёт движок и фабрику сессий из настроек (лениво, один раз)."""
    global _engine, _session_factory
    if _engine is not None:
        return
    settings = get_settings()
    _ensure_db_dir(settings.db_url)
    _engine = create_async_engine(settings.db_url, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def get_engine() -> AsyncEngine:
    """Возвращает движок БД (после ленивой инициализации)."""
    init_db()
    assert _engine is not None
    return _engine


def get_session() -> AsyncSession:
    """Возвращает новую асинхронную сессию."""
    init_db()
    assert _session_factory is not None
    return _session_factory()

