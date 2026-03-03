from decimal import Decimal

from promo_engine.models import Product, ReceiptLine, VatRate


def _product(**kw) -> Product:
    defaults = dict(
        sku="T-1", name="Test", category="cat",
        unit_price_gross=Decimal("100.00"), vat_rate=VatRate.VAT_23, qty=1,
    )
    defaults.update(kw)
    return Product(**defaults)


class TestReceiptLineFactory:
    def test_from_product(self):
        p = _product(unit_price_gross=Decimal("50.00"), qty=3)
        line = ReceiptLine.from_product(p)
        assert line.sku == "T-1"
        assert line.total_before_discount == Decimal("150.00")
        assert line.discount_amount == Decimal("0.00")
        assert line.applied_promotions == []

    def test_is_outlet(self):
        p = _product(category="Outlet")
        line = ReceiptLine.from_product(p)
        assert line.is_outlet is True


class TestAddDiscount:
    def test_single_discount(self):
        line = ReceiptLine.from_product(_product())
        line.add_discount(Decimal("15.00"), "Promo A")
        assert line.discount_amount == Decimal("15.00")
        assert line.applied_promotions == ["Promo A"]

    def test_stacked_discounts(self):
        line = ReceiptLine.from_product(_product())
        line.add_discount(Decimal("10.00"), "A")
        line.add_discount(Decimal("5.00"), "B")
        assert line.discount_amount == Decimal("15.00")
        assert line.applied_promotions == ["A", "B"]

    def test_total_after_discount(self):
        line = ReceiptLine.from_product(_product(unit_price_gross=Decimal("80.00")))
        line.add_discount(Decimal("20.00"), "X")
        assert line.total_after_discount == Decimal("60.00")


class TestClamp:
    def test_clamp_single_item(self):
        """Rabat nie może zbić ceny poniżej 1 zł/szt."""
        line = ReceiptLine.from_product(_product(unit_price_gross=Decimal("10.00")))
        line.discount_amount = Decimal("9.50")
        line.clamp_to_min_price()
        assert line.discount_amount == Decimal("9.00")
        assert line.total_after_discount == Decimal("1.00")

    def test_clamp_multi_qty(self):
        """qty=3, cena 5 PLN → min = 3 zł → max rabat = 12 PLN."""
        line = ReceiptLine.from_product(_product(unit_price_gross=Decimal("5.00"), qty=3))
        line.discount_amount = Decimal("14.00")
        line.clamp_to_min_price()
        assert line.discount_amount == Decimal("12.00")
        assert line.total_after_discount == Decimal("3.00")

    def test_clamp_no_change_when_ok(self):
        line = ReceiptLine.from_product(_product())
        line.discount_amount = Decimal("10.00")
        line.clamp_to_min_price()
        assert line.discount_amount == Decimal("10.00")


class TestNetVat:
    def test_net_and_vat_23(self):
        line = ReceiptLine.from_product(
            _product(unit_price_gross=Decimal("123.00"), vat_rate=VatRate.VAT_23)
        )
        assert line.total_net == Decimal("100.00")
        assert line.total_vat == Decimal("23.00")