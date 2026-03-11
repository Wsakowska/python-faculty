import pytest
from decimal import Decimal

from enums import VatRate
from Zad1.promo_engine.models.product import Product


class TestProductValidation:
    def test_valid_product(self):
        p = Product(
            sku="ABC-1", name="Test", category="cat",
            unit_price_gross=Decimal("50.00"), vat_rate=VatRate.VAT_23, qty=2,
        )
        assert p.sku == "ABC-1"
        assert p.qty == 2

    def test_empty_sku_raises(self):
        with pytest.raises(ValueError, match="SKU nie może być puste"):
            Product(sku="", name="X", category="c",
                    unit_price_gross=Decimal("10"), vat_rate=VatRate.VAT_23, qty=1)

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="Nazwa produktu nie może być pusta"):
            Product(sku="A", name="  ", category="c",
                    unit_price_gross=Decimal("10"), vat_rate=VatRate.VAT_23, qty=1)

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="Cena brutto musi być dodatnia"):
            Product(sku="A", name="X", category="c",
                    unit_price_gross=Decimal("-5"), vat_rate=VatRate.VAT_23, qty=1)

    def test_zero_qty_raises(self):
        with pytest.raises(ValueError, match="Ilość musi być dodatnia"):
            Product(sku="A", name="X", category="c",
                    unit_price_gross=Decimal("10"), vat_rate=VatRate.VAT_23, qty=0)


class TestProductProperties:
    def test_line_total_gross(self):
        p = Product(sku="A", name="X", category="c",
                    unit_price_gross=Decimal("25.50"), vat_rate=VatRate.VAT_23, qty=3)
        assert p.line_total_gross == Decimal("76.50")

    def test_unit_price_net(self):
        p = Product(sku="A", name="X", category="c",
                    unit_price_gross=Decimal("123.00"), vat_rate=VatRate.VAT_23, qty=1)
        assert p.unit_price_net == Decimal("100.00")

    def test_is_outlet_true(self):
        p = Product(sku="A", name="X", category="Outlet",
                    unit_price_gross=Decimal("10"), vat_rate=VatRate.VAT_23, qty=1)
        assert p.is_outlet is True

    def test_is_outlet_false(self):
        p = Product(sku="A", name="X", category="elektronika",
                    unit_price_gross=Decimal("10"), vat_rate=VatRate.VAT_23, qty=1)
        assert p.is_outlet is False