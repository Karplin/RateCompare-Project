import asyncio
import random
from typing import Optional

from app.config.settings import settings
from app.models.request import ExchangeRequest
from app.providers.base import BaseExchangeProvider


class API1Provider(BaseExchangeProvider):
    def __init__(self):
        super().__init__("API1", settings.REQUEST_TIMEOUT)

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

    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        await asyncio.sleep(random.uniform(0.1, 0.3))

        rate_key = (request.source_currency, request.target_currency)

        if rate_key in self.sample_rates:
            base_rate = self.sample_rates[rate_key]
            variation = random.uniform(-0.02, 0.02)
            rate = base_rate * (1 + variation)

            self.logger.info(f"API1 Mock - Rate: {rate} for {rate_key}")
            converted_amount = rate * float(request.amount)
            return converted_amount

        self.logger.warning(f"API1 - Unsupported currency pair: {rate_key}")
        raise ValueError(
            f"Currency conversion from {request.source_currency} to {request.target_currency} is not supported by API1")
