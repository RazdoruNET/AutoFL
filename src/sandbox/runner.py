"""Изолированное выполнение кода из заданий (Этап 6).

Требования к песочнице: без сетевого доступа, лимиты времени и памяти,
изолированный tmpdir, отсутствие доступа к хостовым секретам.
Реализация: Docker-контейнер или subprocess с rlimits.
"""
from dataclasses import dataclass


@dataclass
class SandboxResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""
    timeout: bool = False


async def run_code_in_sandbox(
    code: str,
    timeout_seconds: int = 30,
    memory_mb: int = 256,
) -> SandboxResult:
    """Запуск кода в изолированной среде.

    Полный контур (Docker/subprocess + rlimits + запрет сети) — Этап 6.
    """
    raise NotImplementedError("Этап 6: run_code_in_sandbox")
