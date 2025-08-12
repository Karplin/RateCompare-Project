from decimal import Decimal

import pytest

from common.models.api_formats import (
    API1Request, API1Response,
    API2Request, API2Response,
    API3Request, API3Response, API3ExchangeData
)
from common.providers.api1_provider import API1DirectProvider
from common.providers.api2_provider import API2DirectProvider
from common.providers.api3_provider import API3DirectProvider


@pytest.fixture
def api1_sample_request():
    return API1Request(**{"from": "USD", "to": "EUR", "value": Decimal("100.00")})


@pytest.fixture
def api2_sample_request():
    return API2Request(From="USD", To="EUR", Amount=Decimal("100.00"))


@pytest.fixture
def api3_sample_request():
    return API3Request(
        exchange=API3ExchangeData(
            sourceCurrency="USD",
            targetCurrency="EUR",
            quantity=Decimal("100.00")
        )
    )


class TestDirectProviders:

    @pytest.mark.asyncio
    async def test_api1_direct_provider_success(self, api1_sample_request):
        """Test: API1 direct provider returns valid response in correct format."""
        provider = API1DirectProvider()
        result = await provider.get_exchange_rate(api1_sample_request)

        assert result is not None
        assert isinstance(result, API1Response)
        assert result.rate > 0
        assert isinstance(result.rate, Decimal)

    @pytest.mark.asyncio
    async def test_api2_direct_provider_success(self, api2_sample_request):
        """Test: API2 direct provider returns valid response in correct format."""
        provider = API2DirectProvider()
        result = await provider.get_exchange_rate(api2_sample_request)

        assert result is not None
        assert isinstance(result, API2Response)
        assert result.Result > 0
        assert isinstance(result.Result, Decimal)

    @pytest.mark.asyncio
    async def test_api3_direct_provider_success(self, api3_sample_request):
        """Test: API3 direct provider returns valid response in correct format."""
        provider = API3DirectProvider()

        success = False
        for _ in range(10):
            try:
                result = await provider.get_exchange_rate(api3_sample_request)
                if result:
                    success = True
                    assert isinstance(result, API3Response)
                    assert result.statusCode == 200
                    assert result.data.total > 0
                    assert isinstance(result.data.total, Decimal)
                    break
            except Exception:
                continue

        assert success, "API3 should succeed at least once in 10 attempts"

    @pytest.mark.asyncio
    async def test_providers_handle_unsupported_currencies(self):
        """Test: all providers handle unsupported currency pairs properly."""
        api1_provider = API1DirectProvider()
        api2_provider = API2DirectProvider()
        api3_provider = API3DirectProvider()

        api1_request = API1Request(**{"from": "AED", "to": "QAR", "value": Decimal("10.00")})
        api2_request = API2Request(From="AED", To="QAR", Amount=Decimal("10.00"))
        api3_request = API3Request(
            exchange=API3ExchangeData(sourceCurrency="AED", targetCurrency="QAR", quantity=Decimal("10.00"))
        )

        with pytest.raises(ValueError):
            await api1_provider.get_exchange_rate(api1_request)

        with pytest.raises(ValueError):
            await api2_provider.get_exchange_rate(api2_request)

        with pytest.raises(ValueError):
            await api3_provider.get_exchange_rate(api3_request)

    @pytest.mark.asyncio
    async def test_response_format_accuracy(self, api1_sample_request, api2_sample_request):
        """Test: that responses match expected format specifications."""
        api1_provider = API1DirectProvider()
        api2_provider = API2DirectProvider()

        api1_result = await api1_provider.get_exchange_rate(api1_sample_request)
        assert hasattr(api1_result, 'rate')
        assert not hasattr(api1_result, 'converted_amount')

        api2_result = await api2_provider.get_exchange_rate(api2_sample_request)
        assert hasattr(api2_result, 'Result')
        assert not hasattr(api2_result, 'rate')
