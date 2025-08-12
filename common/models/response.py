from pydantic import BaseModel
from decimal import Decimal


class ExchangeResponse(BaseModel):
    sourceCurrency: str
    targetCurrency: str
    amount: Decimal
    convertedAmount: Decimal
    rate: Decimal
    provider: str
    responseTimeMs: int


class ComparisonData(BaseModel):
    bestOffer: ExchangeResponse
    allOffers: list[ExchangeResponse]
    totalProvidersQueried: int
    successfulProviders: int
    failedProviders: int


class BestExchangeResponse(BaseModel):
    statusCode: int
    message: str
    data: ComparisonData
