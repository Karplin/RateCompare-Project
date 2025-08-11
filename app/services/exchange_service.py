import asyncio
import time
from typing import Optional

from app.models.api_formats import (
    API1Request, API1Response,
    API2Request, API2Response,
    API3Request, API3Response,
    API3ExchangeData
)
from app.models.request import ExchangeRequest
from app.models.response import ExchangeResponse, BestExchangeResponse, ComparisonData
from app.providers.api1_provider import API1DirectProvider
from app.providers.api2_provider import API2DirectProvider
from app.providers.api3_provider import API3DirectProvider
from app.utils.logger import setup_logger


class ExchangeService:
    def __init__(self):
        self.api1_provider = API1DirectProvider()
        self.api2_provider = API2DirectProvider()
        self.api3_provider = API3DirectProvider()

        self.logger = setup_logger(__name__)
        self.logger.info("ExchangeService initialized with direct format providers")

    async def get_best_exchange_rate(self, request: ExchangeRequest) -> BestExchangeResponse:
        self.logger.info(
            f"Getting best exchange rate for {request.amount} {request.source_currency} to {request.target_currency}")

        api1_request = API1Request(
            **{"from": request.source_currency, "to": request.target_currency, "value": request.amount}
        )

        api2_request = API2Request(
            From=request.source_currency,
            To=request.target_currency,
            Amount=request.amount
        )

        api3_request = API3Request(
            exchange=API3ExchangeData(
                sourceCurrency=request.source_currency,
                targetCurrency=request.target_currency,
                quantity=request.amount
            )
        )

        tasks = [
            self._call_api1(api1_request, request),
            self._call_api2(api2_request, request),
            self._call_api3(api3_request, request)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_offers = []
        failed_count = 0
        provider_names = ["API1", "API2", "API3"]

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Provider {provider_names[i]} failed: {str(result)}")
                failed_count += 1
            elif result:
                successful_offers.append(result)
            else:
                failed_count += 1

        if not successful_offers:
            if failed_count == len(provider_names):
                raise ValueError(
                    "All providers failed to provide exchange rates. Please check currency codes and try again.")
            else:
                raise ValueError("No providers returned valid exchange rates")

        best_offer = max(successful_offers, key=lambda x: x.convertedAmount)

        comparison_data = ComparisonData(
            bestOffer=best_offer,
            allOffers=successful_offers,
            totalProvidersQueried=len(provider_names),
            successfulProviders=len(successful_offers),
            failedProviders=failed_count
        )

        return BestExchangeResponse(
            statusCode=200,
            message=f"Exchange comparison completed successfully. Best rate from {best_offer.provider}: {best_offer.rate}",
            data=comparison_data
        )

    async def _call_api1(self, api1_request: API1Request, original_request: ExchangeRequest) -> Optional[
        ExchangeResponse]:
        try:
            start_time = time.time()
            api1_response: API1Response = await self.api1_provider.get_exchange_rate(api1_request)
            response_time = int((time.time() - start_time) * 1000)

            converted_amount = api1_response.rate * original_request.amount

            return ExchangeResponse(
                sourceCurrency=original_request.source_currency,
                targetCurrency=original_request.target_currency,
                amount=original_request.amount,
                convertedAmount=converted_amount,
                rate=api1_response.rate,
                provider="API1",
                responseTimeMs=response_time
            )
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            self.logger.error(f"API1 conversion error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"API1 unexpected error: {str(e)}")
            return None

    async def _call_api2(self, api2_request: API2Request, original_request: ExchangeRequest) -> Optional[
        ExchangeResponse]:
        try:
            start_time = time.time()
            api2_response: API2Response = await self.api2_provider.get_exchange_rate(api2_request)
            response_time = int((time.time() - start_time) * 1000)

            converted_amount = api2_response.Result
            rate = converted_amount / original_request.amount

            return ExchangeResponse(
                sourceCurrency=original_request.source_currency,
                targetCurrency=original_request.target_currency,
                amount=original_request.amount,
                convertedAmount=converted_amount,
                rate=rate,
                provider="API2",
                responseTimeMs=response_time
            )
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            self.logger.error(f"API2 conversion error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"API2 unexpected error: {str(e)}")
            return None

    async def _call_api3(self, api3_request: API3Request, original_request: ExchangeRequest) -> Optional[
        ExchangeResponse]:
        try:
            start_time = time.time()
            api3_response: API3Response = await self.api3_provider.get_exchange_rate(api3_request)
            response_time = int((time.time() - start_time) * 1000)

            converted_amount = api3_response.data.total
            rate = converted_amount / original_request.amount

            return ExchangeResponse(
                sourceCurrency=original_request.source_currency,
                targetCurrency=original_request.target_currency,
                amount=original_request.amount,
                convertedAmount=converted_amount,
                rate=rate,
                provider="API3",
                responseTimeMs=response_time
            )
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            self.logger.error(f"API3 conversion error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"API3 unexpected error: {str(e)}")
            return None
