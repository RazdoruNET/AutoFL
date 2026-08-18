"""Дедупликация заданий (Этап 4).

Ключ уникальности — (platform, external_id). В проде множество виденных ключей
восстанавливается из таблицы candidates; класс при этом остаётся чистым и
тестируемым.
"""
from typing import Iterable, Protocol


class HasIdentity(Protocol):
    platform: str
    external_id: str


class CandidateDedupe:
    def __init__(self, known_keys: set[tuple[str, str]] | None = None) -> None:
        self._seen: set[tuple[str, str]] = set(known_keys or ())

    def is_known(self, platform: str, external_id: str) -> bool:
        return (platform, external_id) in self._seen

    def mark_seen(self, platform: str, external_id: str) -> None:
        self._seen.add((platform, external_id))

    def filter_new(self, candidates: Iterable[HasIdentity]) -> list[HasIdentity]:
        """Возвращает только новые кандидаты и помечает их как увиденные.

        Помечаем ключ сразу при первом вхождении, чтобы дубликаты внутри
        одного пакета не проходили повторно.
        """
        fresh: list[HasIdentity] = []
        for c in candidates:
            if not self.is_known(c.platform, c.external_id):
                self.mark_seen(c.platform, c.external_id)
                fresh.append(c)
        return fresh
