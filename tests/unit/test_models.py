from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.request import ExchangeRequest


class TestModels:

    def test_valid_request_creation(self):
        """Test that valid request is created correctly."""
        request = ExchangeRequest(
            source_currency="USD",
            target_currency="EUR",
            amount=Decimal("100.00")
        )

        assert request.source_currency == "USD"
        assert request.target_currency == "EUR"
        assert request.amount == Decimal("100.00")

    def test_invalid_currency_validation(self):
        """Test that invalid currencies are rejected."""
        with pytest.raises(ValidationError):
            ExchangeRequest(
                source_currency="INVALID",
                target_currency="EUR",
                amount=Decimal("100.00")
            )

    def test_same_currency_validation(self):
        """Test that same source and target currencies are rejected."""
        with pytest.raises(ValidationError):
            ExchangeRequest(
                source_currency="USD",
                target_currency="USD",
                amount=Decimal("100.00")
            )

    def test_negative_amount_validation(self):
        """Test that negative amounts are rejected."""
        with pytest.raises(ValidationError):
            ExchangeRequest(
                source_currency="USD",
                target_currency="EUR",
                amount=Decimal("-100.00")
            )
