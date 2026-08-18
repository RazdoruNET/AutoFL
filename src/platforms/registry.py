"""Фабрика адаптеров платформ (Этап 3).

Адаптеры создаются из переменной PLATFORMS (через запятую).
"""
from typing import Type

from src.config.settings import get_settings
from src.platforms.base import PlatformAdapter
from src.platforms.flru import FlRuAdapter
from src.platforms.kwork import KworkAdapter
from src.platforms.youdо import YouDoAdapter

_REGISTRY: dict[str, Type[PlatformAdapter]] = {
    "kwork": KworkAdapter,
    "flru": FlRuAdapter,
    "youdo": YouDoAdapter,
}


def create_adapters() -> list[PlatformAdapter]:
    """Возвращает адаптеры для площадок из конфигурации."""
    settings = get_settings()
    return [
        _REGISTRY[slug]()
        for slug in settings.platform_list
        if slug in _REGISTRY
    ]
