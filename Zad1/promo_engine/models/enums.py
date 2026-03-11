from decimal import Decimal
from enum import Enum


class LoyaltyLevel(Enum):
    STANDARD = "standard"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class VatRate(Enum):
    VAT_23 = Decimal("0.23")
    VAT_8 = Decimal("0.08")
    VAT_5 = Decimal("0.05")
    VAT_0 = Decimal("0.00")