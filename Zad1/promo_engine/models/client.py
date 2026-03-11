from __future__ import annotations

from dataclasses import dataclass

from Zad1.promo_engine.models.enums import LoyaltyLevel


@dataclass(frozen=True)
class Client:

    id_client: str
    loyalty_level: LoyaltyLevel = LoyaltyLevel.STANDARD

    def __post_init__(self) -> None:
        if not self.id_client or not self.id_client.strip():
            raise ValueError("ID klienta nie może być puste.")