from decimal import Decimal

import pytest

from common.models.request import ExchangeRequest
from common.services.exchange_service import ExchangeService


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
        """Test: Service selects the provider with highest converted amount."""
        service = ExchangeService()

        class MockAPI1Provider:
            def __init__(self, name, converted_amount):
                self.name = name
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                from common.models.api_formats import API1Response
                rate = Decimal(str(self.converted_amount)) / sample_request.amount
                return API1Response(rate=rate)

        class MockAPI2Provider:
            def __init__(self, name, converted_amount):
                self.name = name
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                from common.models.api_formats import API2Response
                return API2Response(Result=Decimal(str(self.converted_amount)))

        class MockAPI3Provider:
            def __init__(self, name, converted_amount):
                self.name = name
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                from common.models.api_formats import API3Response, API3DataResponse
                return API3Response(
                    statusCode=200,
                    message="Success",
                    data=API3DataResponse(total=Decimal(str(self.converted_amount)))
                )

        service.api1_provider = MockAPI1Provider("API1", 85.0)
        service.api2_provider = MockAPI2Provider("API2", 87.5)
        service.api3_provider = MockAPI3Provider("API3", 86.0)

        result = await service.get_best_exchange_rate(sample_request)
        assert result.statusCode == 200
        assert "API2" in result.message
        assert result.data.bestOffer.provider == "API2"
        assert result.data.bestOffer.convertedAmount == Decimal("87.5")
        assert result.data.successfulProviders == 3
        assert result.data.failedProviders == 0

    @pytest.mark.asyncio
    async def test_service_resilience_with_failures(self, sample_request):
        """Test: Service works when some providers fail."""
        service = ExchangeService()

        class MockAPI1Provider:
            def __init__(self, name, should_fail=False, converted_amount=None):
                self.name = name
                self.should_fail = should_fail
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                if self.should_fail:
                    raise Exception("API unavailable")

                from common.models.api_formats import API1Response
                rate = Decimal(str(self.converted_amount)) / sample_request.amount
                return API1Response(rate=rate)

        class MockAPI2Provider:
            def __init__(self, name, should_fail=False, converted_amount=None):
                self.name = name
                self.should_fail = should_fail
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                if self.should_fail:
                    raise Exception("API unavailable")

                from common.models.api_formats import API2Response
                return API2Response(Result=Decimal(str(self.converted_amount)))

        class MockAPI3Provider:
            def __init__(self, name, should_fail=False, converted_amount=None):
                self.name = name
                self.should_fail = should_fail
                self.converted_amount = converted_amount

            async def get_exchange_rate(self, request):
                if self.should_fail:
                    raise Exception("API unavailable")

                from common.models.api_formats import API3Response, API3DataResponse
                return API3Response(
                    statusCode=200,
                    message="Success",
                    data=API3DataResponse(total=Decimal(str(self.converted_amount)))
                )

        service.api1_provider = MockAPI1Provider("API1", should_fail=False, converted_amount=85.0)
        service.api2_provider = MockAPI2Provider("API2", should_fail=True, converted_amount=None)
        service.api3_provider = MockAPI3Provider("API3", should_fail=False, converted_amount=86.0)

        result = await service.get_best_exchange_rate(sample_request)
        assert result.statusCode == 200
        assert result.data.bestOffer.provider == "API3"
        assert result.data.successfulProviders == 2
        assert result.data.failedProviders == 1

    @pytest.mark.asyncio
    async def test_service_all_providers_fail(self, sample_request):
        """Test: Service raises error when all providers fail."""
        service = ExchangeService()

        class MockAPI1Provider:
            def __init__(self, name):
                self.name = name

            async def get_exchange_rate(self, request):
                raise Exception("API unavailable")

        class MockAPI2Provider:
            def __init__(self, name):
                self.name = name

            async def get_exchange_rate(self, request):
                raise Exception("API unavailable")

        class MockAPI3Provider:
            def __init__(self, name):
                self.name = name

            async def get_exchange_rate(self, request):
                raise Exception("API unavailable")

        service.api1_provider = MockAPI1Provider("API1")
        service.api2_provider = MockAPI2Provider("API2")
        service.api3_provider = MockAPI3Provider("API3")

        with pytest.raises(ValueError, match="All providers failed"):
            await service.get_best_exchange_rate(sample_request)

    @pytest.mark.asyncio
    async def test_service_with_unsupported_currencies(self, unsupported_request):
        """Test: Service handles unsupported currency pairs correctly."""
        service = ExchangeService()

        with pytest.raises(ValueError, match="All providers failed"):
            await service.get_best_exchange_rate(unsupported_request)
