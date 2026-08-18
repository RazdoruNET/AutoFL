"""Зашифрованное хранилище чувствительных данных (Трек B1, B6).

Fernet-шифрование (cryptography). Ключ — из VAULT_KEY либо автогенерируется
в data/vault.key (каталог data/ исключён из git).
"""
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from src.config.settings import get_settings
from src.observability import get_logger

logger = get_logger("autofl.vault")

_KEY_FILE = Path(__file__).resolve().parents[1] / "data" / "vault.key"


def _load_key() -> bytes:
    settings = get_settings()
    if settings.vault_key:
        return settings.vault_key.encode("utf-8")
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_bytes(key)
    logger.warning("Сгенерирован новый ключ vault: %s", _KEY_FILE)
    return key


def _fernet() -> Fernet:
    return Fernet(_load_key())


def encrypt_text(plain: str) -> str:
    """Шифрует строку; возвращает токен (str)."""
    return _fernet().encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str) -> str:
    """Расшифровывает токен; при неверном ключе — ValueError."""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Неверный ключ vault или повреждённый токен") from exc


def mask_card_number(pan: str) -> str:
    """Маскирует номер карты: 1234 **** **** 5678."""
    pan = pan.replace(" ", "").replace("-", "")
    if len(pan) < 8:
        return "****"
    return f"{pan[:4]} **** **** {pan[-4:]}"
