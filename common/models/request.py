from decimal import Decimal
from typing import Set

from pydantic import BaseModel, Field, field_validator, model_validator

VALID_CURRENCIES: Set[str] = {
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD", "SEK", "NOK",
    "DKK", "PLN", "CZK", "HUF", "RUB", "CNY", "HKD", "SGD", "KRW", "INR",
    "BRL", "MXN", "ZAR", "TRY", "ILS", "AED", "SAR", "QAR", "KWD", "BHD"
}


class ExchangeRequest(BaseModel):
    source_currency: str = Field(..., description="Source currency code (e.g., USD)", min_length=3, max_length=3)
    target_currency: str = Field(..., description="Target currency code (e.g., EUR)", min_length=3, max_length=3)
    amount: Decimal = Field(..., description="Amount to convert", gt=0)

    @field_validator('source_currency')
    @classmethod
    def validate_source_currency(cls, v: str) -> str:
        if not v:
            raise ValueError("Source currency is required")

        v = v.upper().strip()

        if len(v) != 3:
            raise ValueError("Source currency must be exactly 3 characters (e.g., USD, EUR, GBP)")

        if not v.isalpha():
            raise ValueError("Source currency must contain only letters")

        if v not in VALID_CURRENCIES:
            raise ValueError(
                f"Invalid source currency '{v}'. \nSupported currencies: {', '.join(sorted(VALID_CURRENCIES))}")

        return v

    @field_validator('target_currency')
    @classmethod
    def validate_target_currency(cls, v: str) -> str:
        if not v:
            raise ValueError("Target currency is required")

        v = v.upper().strip()

        if len(v) != 3:
            raise ValueError("Target currency must be exactly 3 characters (e.g., EUR)")

        if not v.isalpha():
            raise ValueError("Target currency must contain only letters")

        if v not in VALID_CURRENCIES:
            raise ValueError(
                f"Invalid target currency '{v}'. Supported currencies: {', '.join(sorted(VALID_CURRENCIES))}")

        return v

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")

        if v > 1000000:
            raise ValueError("Amount cannot exceed 1,000,000")

        if v.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")

        return v

    @model_validator(mode='after')
    def validate_different_currencies(self) -> 'ExchangeRequest':
        if self.source_currency == self.target_currency:
            raise ValueError("Source and target currencies cannot be the same")
        return self
