from decimal import Decimal

import pytest

from app.models.request import ExchangeRequest
from app.providers.api1_provider import API1Provider
from app.providers.api2_provider import API2Provider
from app.providers.api3_provider import API3Provider


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


class TestProviders:

    @pytest.mark.asyncio
    async def test_api1_provider_success(self, sample_request):
        """Test 1: API1 provider returns valid exchange rate for supported currency pair."""
        provider = API1Provider()
        result = await provider.get_exchange_rate(sample_request)

        assert result is not None
        assert result.provider == "API1"
        assert result.converted_amount > 0
        assert result.rate > 0

    @pytest.mark.asyncio
    async def test_api2_provider_success(self, sample_request):
        """Test 2: API2 provider returns valid exchange rate for supported currency pair."""
        provider = API2Provider()
        result = await provider.get_exchange_rate(sample_request)

        assert result is not None
        assert result.provider == "API2"
        assert result.converted_amount > 0
        assert result.rate > 0

    @pytest.mark.asyncio
    async def test_api3_provider_success(self, sample_request):
        """Test 3: API3 provider handles success and random failures correctly."""
        provider = API3Provider()

        success_found = False
        for _ in range(10):
            try:
                result = await provider.get_exchange_rate(sample_request)
                if result:
                    assert result.provider == "API3"
                    assert result.converted_amount > 0
                    success_found = True
                    break
            except:
                continue

        assert success_found, "API3 should succeed at least once"

    @pytest.mark.asyncio
    async def test_providers_handle_unsupported_currencies(self, unsupported_request):
        """Test 4: All providers return None for unsupported currency pairs."""
        api1 = API1Provider()
        api2 = API2Provider()
        api3 = API3Provider()

        result1 = await api1.get_exchange_rate(unsupported_request)
        result2 = await api2.get_exchange_rate(unsupported_request)
        result3 = await api3.get_exchange_rate(unsupported_request)

        assert result1 is None
        assert result2 is None
        assert result3 is None

    @pytest.mark.asyncio
    async def test_rate_calculation_accuracy(self, sample_request):
        """Test 5: Rate calculations are mathematically correct."""
        provider = API1Provider()
        result = await provider.get_exchange_rate(sample_request)

        assert result is not None
        expected_converted = result.rate * result.amount
        assert abs(result.converted_amount - expected_converted) < Decimal("0.01")
