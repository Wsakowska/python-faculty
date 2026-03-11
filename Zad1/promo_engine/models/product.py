from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from enums import VatRate


@dataclass(frozen=True)
class Product:
    #Produkt w koszyku sklepu internetowego.

    sku: str
    name: str
    category: str
    unit_price_gross: Decimal
    vat_rate: VatRate
    qty: int

    def __post_init__(self) -> None:
        if not self.sku or not self.sku.strip():
            raise ValueError("SKU nie może być puste.")
        if not self.name or not self.name.strip():
            raise ValueError("Nazwa produktu nie może być pusta.")
        if self.unit_price_gross <= 0:
            raise ValueError(
                f"Cena brutto musi być dodatnia, otrzymano: {self.unit_price_gross}"
            )
        if self.qty <= 0:
            raise ValueError(
                f"Ilość musi być dodatnia, otrzymano: {self.qty}"
            )

    @property
    def line_total_gross(self) -> Decimal:
        #Wartość brutto pozycji (cena × ilość).
        return self.unit_price_gross * self.qty

    @property
    def unit_price_net(self) -> Decimal:
        #Cena netto za sztukę.
        return (self.unit_price_gross / (1 + self.vat_rate.value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def is_outlet(self) -> bool:
        #Czy produkt należy do kategorii outlet.
        return self.category.lower() == "outlet"