import asyncio
import random
from typing import Optional

from app.config.settings import settings
from app.models.request import ExchangeRequest
from app.providers.base import BaseExchangeProvider


class API3Provider(BaseExchangeProvider):
    def __init__(self):
        super().__init__("API3", settings.REQUEST_TIMEOUT)

        self.sample_rates = {
            ("USD", "EUR"): 0.86,
            ("USD", "GBP"): 0.735,
            ("USD", "JPY"): 109.8,
            ("EUR", "USD"): 1.16,
            ("EUR", "GBP"): 0.87,
            ("GBP", "USD"): 1.36,
            ("GBP", "EUR"): 1.15,
            ("JPY", "USD"): 0.0091,
        }

    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        await asyncio.sleep(random.uniform(0.05, 0.2))

        if random.random() < 0.1:
            self.logger.warning("API3 Mock - Simulated temporary failure")
            raise Exception("API3 temporarily unavailable")

        rate_key = (request.source_currency, request.target_currency)

        if rate_key in self.sample_rates:
            base_rate = self.sample_rates[rate_key]
            variation = random.uniform(-0.025, 0.025)
            rate = base_rate * (1 + variation)

            converted_amount = rate * float(request.amount)
            self.logger.info(f"API3 Mock (JSON Nested) - Total: {converted_amount} for {rate_key}")
            return converted_amount

        self.logger.warning(f"API3 - Unsupported currency pair: {rate_key}")
        raise ValueError(
            f"Currency conversion from {request.source_currency} to {request.target_currency} is not supported by API3")
