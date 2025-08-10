from typing import Optional

from app.config.settings import settings
from app.models.request import ExchangeRequest
from app.providers.base import BaseExchangeProvider


class API1Provider(BaseExchangeProvider):
    def __init__(self):
        super().__init__("API1", settings.REQUEST_TIMEOUT)
        self.url = settings.API1_URL
        self.api_key = settings.API1_API_KEY

    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        async with self._create_client() as client:
            payload = {
                "from": request.source_currency,
                "to": request.target_currency,
                "value": float(request.amount),
                "api_key": self.api_key
            }

            response = await client.post(self.url, json=payload)
            response.raise_for_status()

            data = response.json()
            if "rate" in data:
                return float(data["rate"]) * float(request.amount)

            return None
