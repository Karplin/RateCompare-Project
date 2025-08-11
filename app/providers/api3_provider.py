import asyncio
import random
from decimal import Decimal

from app.models.api_formats import API3Request, API3Response, API3DataResponse
from app.utils.logger import setup_logger


class API3DirectProvider:
    def __init__(self):
        self.name = "API3"
        self.logger = setup_logger(f"{__name__}.{self.name}_Direct")

        self.sample_rates = {
            ("USD", "EUR"): 0.865,
            ("USD", "GBP"): 0.735,
            ("USD", "JPY"): 110.5,
            ("EUR", "USD"): 1.155,
            ("EUR", "GBP"): 0.855,
            ("GBP", "USD"): 1.365,
            ("GBP", "EUR"): 1.175,
            ("JPY", "USD"): 0.0091,
        }

    async def get_exchange_rate(self, request: API3Request) -> API3Response:
        await asyncio.sleep(random.uniform(0.15, 0.35))

        rate_key = (request.exchange.sourceCurrency, request.exchange.targetCurrency)

        if rate_key in self.sample_rates:
            base_rate = self.sample_rates[rate_key]
            variation = random.uniform(-0.025, 0.025)
            rate = base_rate * (1 + variation)

            self.logger.info(f"API3 - Rate: {rate} for {rate_key}")

            converted_amount = rate * float(request.exchange.quantity)

            return API3Response(
                statusCode=200,
                message="Exchange completed successfully",
                data=API3DataResponse(total=Decimal(str(converted_amount)))
            )

        self.logger.warning(f"API3 - Unsupported currency pair: {rate_key}")
        raise ValueError(f"Currency conversion from {request.exchange.sourceCurrency} to {request.exchange.targetCurrency} is not supported by API3")
