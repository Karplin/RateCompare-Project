from pydantic import BaseModel
from decimal import Decimal


class ExchangeResponse(BaseModel):
    source_currency: str
    target_currency: str
    amount: Decimal
    converted_amount: Decimal
    rate: Decimal
    provider: str
    response_time_ms: int


class BestExchangeResponse(BaseModel):
    best_offer: ExchangeResponse
    all_offers: list[ExchangeResponse]
    total_providers_queried: int
    successful_providers: int
    failed_providers: int
