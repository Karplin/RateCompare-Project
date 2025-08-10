import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

import httpx

from app.models.request import ExchangeRequest
from app.models.response import ExchangeResponse
from app.utils.logger import setup_logger


class BaseExchangeProvider(ABC):
    def __init__(self, name: str, timeout: int = 10):
        self.name = name
        self.timeout = timeout
        self.logger = setup_logger(f"{__name__}.{name}")

    async def get_exchange_rate(self, request: ExchangeRequest) -> Optional[ExchangeResponse]:
        start_time = time.time()

        try:
            self.logger.info(f"Requesting exchange rate from {self.name}")
            result = await self._make_request(request)

            if result:
                response_time = int((time.time() - start_time) * 1000)
                converted_amount = Decimal(str(result))
                rate = converted_amount / request.amount

                return ExchangeResponse(
                    source_currency=request.source_currency,
                    target_currency=request.target_currency,
                    amount=request.amount,
                    converted_amount=converted_amount,
                    rate=rate,
                    provider=self.name,
                    response_time_ms=response_time
                )

        except Exception as e:
            self.logger.error(f"Error getting exchange rate from {self.name}: {str(e)}")

        return None

    @abstractmethod
    async def _make_request(self, request: ExchangeRequest) -> Optional[float]:
        pass

    def _create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.timeout)
