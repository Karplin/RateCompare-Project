import asyncio
import random
from decimal import Decimal

from app.models.api_formats import API2Request, API2Response
from app.utils.logger import setup_logger


class API2DirectProvider:
    def __init__(self):
        self.name = "API2"
        self.logger = setup_logger(f"{__name__}.{self.name}_Direct")

        self.sample_rates = {
            ("USD", "EUR"): 0.86,
            ("USD", "GBP"): 0.74,
            ("USD", "JPY"): 111.0,
            ("EUR", "USD"): 1.16,
            ("EUR", "GBP"): 0.87,
            ("GBP", "USD"): 1.35,
            ("GBP", "EUR"): 1.15,
            ("JPY", "USD"): 0.009,
        }

    async def get_exchange_rate(self, request: API2Request) -> API2Response:
        await asyncio.sleep(random.uniform(0.2, 0.4))

        rate_key = (request.From, request.To)

        if rate_key in self.sample_rates:
            base_rate = self.sample_rates[rate_key]
            variation = random.uniform(-0.015, 0.015)
            rate = base_rate * (1 + variation)

            self.logger.info(f"API2 - Rate: {rate} for {rate_key}")

            return API2Response(Result=Decimal(str(rate)))

        self.logger.warning(f"API2 - Unsupported currency pair: {rate_key}")
        raise ValueError(f"Currency conversion from {request.From} to {request.To} is not supported by API2")
