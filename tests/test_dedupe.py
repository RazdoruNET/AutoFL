"""Дедупликация заданий (Этап 4)."""
from src.discovery.dedupe import CandidateDedupe
from src.platforms.base import TaskCandidate


def _cand(external_id: str) -> TaskCandidate:
    return TaskCandidate(
        platform="kwork",
        external_id=external_id,
        url=f"https://kwork.example/t/{external_id}",
        title="Задание",
    )


def test_filter_new_dedupes():
    dedupe = CandidateDedupe()
    items = [_cand("1"), _cand("1"), _cand("2")]
    fresh = dedupe.filter_new(items)
    assert [c.external_id for c in fresh] == ["1", "2"]
    # повторный прогон с теми же заданиями — ничего нового
    assert dedupe.filter_new(items) == []


def test_known_keys_from_db():
    dedupe = CandidateDedupe(known_keys={("kwork", "old")})
    assert dedupe.is_known("kwork", "old")
    assert not dedupe.is_known("kwork", "new")
    assert not dedupe.is_known("flru", "old")  # ключ включает площадку
