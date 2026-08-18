"""Источники средств: карта/СБП (Трек B1).

PAN шифруется через src/security/vault.py; наружу — только masked-вид.
"""
from dataclasses import dataclass, field

from src.security.vault import encrypt_text, mask_card_number


@dataclass
class CardSource:
    kind: str = "card"  # card | sbp
    holder: str = ""
    bank: str = ""
    pan: str = ""  # полный номер — только при вводе; в БД уходит pan_enc
    sbp_phone: str = ""
    status: str = "active"
    is_default: bool = False
    _pan_enc: str = field(default="", repr=False)

    def to_record(self) -> dict:
        """Данные для сохранения в FundingSource (PAN — зашифрован)."""
        enc = self._pan_enc or (encrypt_text(self.pan) if self.pan else "")
        return {
            "kind": self.kind,
            "holder": self.holder,
            "bank": self.bank,
            "pan_enc": enc,
            "sbp_phone": self.sbp_phone,
            "masked": mask_card_number(self.pan) if self.pan else "",
            "status": self.status,
            "is_default": self.is_default,
        }


def default_requisites_from_settings() -> dict:
    """Собирает реквизиты по умолчанию из настроек (.env)."""
    from src.config.settings import get_settings

    s = get_settings()
    return {
        "holder": s.default_card_holder,
        "bank": s.default_card_bank,
        "sbp_phone": s.default_card_sbp_phone,
    }
