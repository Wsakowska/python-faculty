import pytest

from Zad1.promo_engine.models import Client, LoyaltyLevel


class TestClientValidation:
    def test_valid_client(self):
        c = Client(id_client="K-001", loyalty_level=LoyaltyLevel.GOLD)
        assert c.id_client == "K-001"
        assert c.loyalty_level == LoyaltyLevel.GOLD

    def test_default_loyalty(self):
        c = Client(id_client="K-002")
        assert c.loyalty_level == LoyaltyLevel.STANDARD

    def test_empty_id_raises(self):
        with pytest.raises(ValueError, match="ID klienta nie może być puste"):
            Client(id_client="  ")

    def test_blank_id_raises(self):
        with pytest.raises(ValueError, match="ID klienta nie może być puste"):
            Client(id_client="")