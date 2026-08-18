"""Верификация и защита финансовых данных (Трек B1)."""
from src.security.vault import decrypt_text, encrypt_text, mask_card_number


def test_roundtrip():
    token = encrypt_text("секрет")
    assert decrypt_text(token) == "секрет"


def test_roundtrip_card_pan():
    pan = "4276123456781234"
    token = encrypt_text(pan)
    assert decrypt_text(token) == pan
    assert token != pan  # PAN не хранится открытым текстом


def test_mask_card_number():
    assert mask_card_number("4276123456781234") == "4276 **** **** 1234"
    assert mask_card_number("4276 1234 5678 1234") == "4276 **** **** 1234"
    assert mask_card_number("1234") == "****"
