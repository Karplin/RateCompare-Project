import httpx
from typing import Optional
from app.providers.base import BaseExchangeProvider
from app.models.request import ExchangeRequest
from app.config.settings import settings


class API2Provider(BaseExchangeProvider):
    def __init__(self):
        super().__init__("API2", settings.REQUEST_TIMEOUT)
        self.url = settings.API2_URL
        self.api_key = settings.API2_API_KEY

    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        async with self._create_client() as client:
            xml_payload = f"""<XML>
                <From>{request.source_currency}</From>
                <To>{request.target_currency}</To>
                <Amount>{request.amount}</Amount>
                <ApiKey>{self.api_key}</ApiKey>
            </XML>"""

            headers = {"Content-Type": "application/xml"}

            response = await client.post(self.url, content=xml_payload, headers=headers)
            response.raise_for_status()

            content = response.text
            start = content.find("<Result>") + 8
            end = content.find("</Result>")

            if start > 7 and end > start:
                return float(content[start:end])

            return None
