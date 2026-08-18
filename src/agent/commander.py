"""Командир агента: NL-команды через Telegram-админа (Трек B7).

Принимает команды оператора («заведи учётные записи»), запускает planner
и докладывает результат.
"""
from __future__ import annotations


class AgentCommander:
    async def handle_command(self, text: str) -> str:
        """Обрабатывает команду оператора; возвращает ответ-отчёт."""
        raise NotImplementedError("Этап B7: обработка команд оператора")
