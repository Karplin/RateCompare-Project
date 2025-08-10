import asyncio
import random
from typing import Optional

from app.config.settings import settings
from app.models.request import ExchangeRequest
from app.providers.base import BaseExchangeProvider


class API2Provider(BaseExchangeProvider):
    def __init__(self):
        super().__init__("API2", settings.REQUEST_TIMEOUT)

        self.sample_rates = {
            ("USD", "EUR"): 0.87,
            ("USD", "GBP"): 0.74,
            ("USD", "JPY"): 111.5,
            ("EUR", "USD"): 1.15,
            ("EUR", "GBP"): 0.85,
            ("GBP", "USD"): 1.35,
            ("GBP", "EUR"): 1.18,
            ("JPY", "USD"): 0.0089,
        }

    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        await asyncio.sleep(random.uniform(0.2, 0.5))

        rate_key = (request.source_currency, request.target_currency)

        if rate_key in self.sample_rates:
            base_rate = self.sample_rates[rate_key]
            variation = random.uniform(-0.015, 0.015)
            rate = base_rate * (1 + variation)

            converted_amount = rate * float(request.amount)
            self.logger.info(f"API2 Mock (XML) - Amount: {converted_amount} for {rate_key}")
            return converted_amount

        self.logger.warning(f"API2 - Unsupported currency pair: {rate_key}")
        raise ValueError(
            f"Currency conversion from {request.source_currency} to {request.target_currency} is not supported by API2")
