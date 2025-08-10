from pydantic import BaseModel, Field
from decimal import Decimal

class ExchangeRequest(BaseModel):
    source_currency: str = Field(..., description="Source currency code (e.g., USD)")
    target_currency: str = Field(..., description="Target currency code (e.g., EUR)")
    amount: Decimal = Field(..., description="Amount to convert", gt=0)
