from decimal import Decimal

import pytest

from app.models.request import ExchangeRequest
from app.services.exchange_service import ExchangeService


@pytest.fixture
def sample_request():
    return ExchangeRequest(
        source_currency="USD",
        target_currency="EUR",
        amount=Decimal("100.00")
    )


@pytest.fixture
def unsupported_request():
    return ExchangeRequest(
        source_currency="AED",
        target_currency="QAR",
        amount=Decimal("100.00")
    )


class TestExchangeService:

    @pytest.mark.asyncio
    async def test_service_selects_best_rate(self, sample_request):
        """Test 6: Service selects the provider with highest converted amount."""
        service = ExchangeService()

        class MockProvider:
            def __init__(self, name, converted_amount):
                self.name = name
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                from app.models.response import ExchangeResponse
                return ExchangeResponse(
                    source_currency=request.source_currency,
                    target_currency=request.target_currency,
                    amount=request.amount,
                    converted_amount=Decimal(str(self.converted_amount)),
                    rate=Decimal(str(self.converted_amount)) / request.amount,
                    provider=self.name,
                    response_time_ms=100
                )

        service.providers = [
            MockProvider("API1", 85.0),
            MockProvider("API2", 87.5),
            MockProvider("API3", 86.0)
        ]

        result = await service.get_best_exchange_rate(sample_request)
        assert result.best_offer.provider == "API2"
        assert result.best_offer.converted_amount == Decimal("87.5")

    @pytest.mark.asyncio
    async def test_service_resilience_with_failures(self, sample_request):
        """Test 7: Service works when some providers fail."""
        service = ExchangeService()

        class MockProvider:
            def __init__(self, name, should_fail=False, converted_amount=None):
                self.name = name
                self.should_fail = should_fail
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                if self.should_fail:
                    raise Exception("API unavailable")

                from app.models.response import ExchangeResponse
                return ExchangeResponse(
                    source_currency=request.source_currency,
                    target_currency=request.target_currency,
                    amount=request.amount,
                    converted_amount=Decimal(str(self.converted_amount)),
                    rate=Decimal(str(self.converted_amount)) / request.amount,
                    provider=self.name,
                    response_time_ms=100
                )

        service.providers = [
            MockProvider("API1", should_fail=False, converted_amount=85.0),
            MockProvider("API2", should_fail=True),
            MockProvider("API3", should_fail=False, converted_amount=86.0)
        ]

        result = await service.get_best_exchange_rate(sample_request)
        assert result.best_offer.provider == "API3"
        assert result.successful_providers == 2
        assert result.failed_providers == 1

    @pytest.mark.asyncio
    async def test_service_all_providers_fail(self, sample_request):
        """Test 8: Service raises error when all providers fail."""
        service = ExchangeService()

        class MockProvider:
            def __init__(self, name):
                self.name = name

            async def get_exchange_rate(self, request):
                raise Exception("API unavailable")

        service.providers = [MockProvider("API1"), MockProvider("API2"), MockProvider("API3")]

        with pytest.raises(ValueError, match="All providers failed"):
            await service.get_best_exchange_rate(sample_request)

    @pytest.mark.asyncio
    async def test_service_with_real_providers(self, sample_request):
        """Test 9: Service works with actual mock providers."""
        service = ExchangeService()
        result = await service.get_best_exchange_rate(sample_request)

        assert result is not None
        assert result.best_offer.provider in ["API1", "API2", "API3"]
        assert result.total_providers_queried == 3
        assert result.successful_providers > 0

    @pytest.mark.asyncio
    async def test_service_with_unsupported_currencies(self, unsupported_request):
        """Test 10: Service handles unsupported currency pairs correctly."""
        service = ExchangeService()

        with pytest.raises(ValueError, match="All providers failed"):
            await service.get_best_exchange_rate(unsupported_request)
