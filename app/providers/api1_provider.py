import asyncio
import random
from decimal import Decimal

from app.models.api_formats import API1Request, API1Response
from app.utils.logger import setup_logger


class API1DirectProvider:
    def __init__(self):
        self.name = "API1"
        self.logger = setup_logger(f"{__name__}.{self.name}_Direct")

        self.sample_rates = {
            ("USD", "EUR"): 0.85,
            ("USD", "GBP"): 0.73,
            ("USD", "JPY"): 110.0,
            ("EUR", "USD"): 1.18,
            ("EUR", "GBP"): 0.86,
            ("GBP", "USD"): 1.37,
            ("GBP", "EUR"): 1.16,
            ("JPY", "USD"): 0.009,
        }

    async def get_exchange_rate(self, request: API1Request) -> API1Response:
        await asyncio.sleep(random.uniform(0.1, 0.3))

        rate_key = (request.from_, request.to)

        if rate_key in self.sample_rates:
            base_rate = self.sample_rates[rate_key]
            variation = random.uniform(-0.02, 0.02)
            rate = base_rate * (1 + variation)

            self.logger.info(f"API1 - Rate: {rate} for {rate_key}")

            return API1Response(rate=Decimal(str(rate)))

        self.logger.warning(f"API1 - Unsupported currency pair: {rate_key}")
        raise ValueError(f"Currency conversion from {request.from_} to {request.to} is not supported by API1")
