from typing import Optional

from app.config.settings import settings
from app.models.request import ExchangeRequest
from app.providers.base import BaseExchangeProvider


class API3Provider(BaseExchangeProvider):
    def __init__(self):
        super().__init__("API3", settings.REQUEST_TIMEOUT)
        self.url = settings.API3_URL
        self.api_key = settings.API3_API_KEY

    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        async with self._create_client() as client:
            payload = {
                "exchange": {
                    "sourceCurrency": request.source_currency,
                    "targetCurrency": request.target_currency,
                    "quantity": float(request.amount)
                },
                "api_key": self.api_key
            }

            response = await client.post(self.url, json=payload)
            response.raise_for_status()

            data = response.json()

            if data.get("statusCode") == 200 and "data" in data and "total" in data["data"]:
                return float(data["data"]["total"])

            return None
