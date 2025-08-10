import asyncio
from app.models.request import ExchangeRequest
from app.models.response import BestExchangeResponse
from app.providers.api1_provider import API1Provider
from app.providers.api2_provider import API2Provider
from app.providers.api3_provider import API3Provider
from app.utils.logger import setup_logger


class ExchangeService:
    def __init__(self):
        self.providers = [
            API1Provider(),
            API2Provider(),
            API3Provider()
        ]
        self.logger = setup_logger(__name__)

    async def get_best_exchange_rate(self, request: ExchangeRequest) -> BestExchangeResponse:
        self.logger.info(
            f"Getting best exchange rate for {request.amount} {request.source_currency} to {request.target_currency}")

        tasks = [
            provider.get_exchange_rate(request)
            for provider in self.providers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_offers = []
        failed_count = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Provider {self.providers[i].name} failed: {str(result)}")
                failed_count += 1
            elif result:
                successful_offers.append(result)
            else:
                failed_count += 1

        if not successful_offers:
            raise ValueError("No providers returned valid exchange rates")

        best_offer = max(successful_offers, key=lambda x: x.converted_amount)

        return BestExchangeResponse(
            best_offer=best_offer,
            all_offers=successful_offers,
            total_providers_queried=len(self.providers),
            successful_providers=len(successful_offers),
            failed_providers=failed_count
        )
