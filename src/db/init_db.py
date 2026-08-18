"""Создание схемы БД (create_all) — временно до ввода Alembic-миграций."""
import asyncio

from src.db.models import Base
from src.db.session import get_engine


async def create_all() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_all())
    print("БД инициализирована.")

