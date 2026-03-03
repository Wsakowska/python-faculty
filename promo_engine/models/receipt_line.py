from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

from promo_engine.models.enums import VatRate
from promo_engine.models.product import Product


@dataclass
class ReceiptLine:
    #Pojedyncza pozycja na paragonie.
    sku: str
    name: str
    category: str
    qty: int
    unit_price_gross: Decimal
    vat_rate: VatRate
    total_before_discount: Decimal
    discount_amount: Decimal = Decimal("0.00")
    applied_promotions: list[str] = field(default_factory=list)

    @classmethod
    def from_product(cls, product: Product) -> ReceiptLine:
        #Factory method - tworzy linię paragonu z produktu (bez rabatów)
        return cls(
            sku=product.sku,
            name=product.name,
            category=product.category,
            qty=product.qty,
            unit_price_gross=product.unit_price_gross,
            vat_rate=product.vat_rate,
            total_before_discount=product.line_total_gross,
        )

    @property
    def is_outlet(self) -> bool:
        return self.category.lower() == "outlet"

    @property
    def total_after_discount(self) -> Decimal:
        return self.total_before_discount - self.discount_amount

    @property
    def total_net(self) -> Decimal:
        return (self.total_after_discount / (1 + self.vat_rate.value)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def total_vat(self) -> Decimal:
        return self.total_after_discount - self.total_net

    def add_discount(self, amount: Decimal, promo_description: str) -> None:
        #Dodaje rabat do linii paragonu.
        self.discount_amount += amount
        self.applied_promotions.append(promo_description)

    def clamp_to_min_price(self, min_unit_price: Decimal = Decimal("1.00")) -> None:
        #Ogranicza rabat — cena nie może spaść poniżej minimum za sztukę.
        min_total = min_unit_price * self.qty
        max_allowed = max(self.total_before_discount - min_total, Decimal("0.00"))
        if self.discount_amount > max_allowed:
            self.discount_amount = max_allowed