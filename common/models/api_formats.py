from decimal import Decimal
from pydantic import BaseModel, Field
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, tostring


class API1Request(BaseModel):
    from_: str = Field(..., alias="from", description="Source currency (e.g., USD)", min_length=3, max_length=3)
    to: str = Field(..., description="Target currency (e.g., EUR)", min_length=3, max_length=3)
    value: Decimal = Field(..., description="Amount to convert", gt=0)

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "from": "USD",
                "to": "EUR",
                "value": 100.00
            }
        }
    }


class API1Response(BaseModel):
    rate: Decimal = Field(..., description="Exchange rate")

    model_config = {
        "json_schema_extra": {
            "example": {
                "rate": 0.85
            }
        }
    }


class API2Request(BaseModel):
    From: str = Field(..., description="Source currency (e.g., USD)", min_length=3, max_length=3)
    To: str = Field(..., description="Target currency (e.g., EUR)", min_length=3, max_length=3)
    Amount: Decimal = Field(..., description="Amount to convert", gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "From": "USD",
                "To": "EUR",
                "Amount": 100.00
            },
            "description": "Will be converted to XML format: <XML><From>USD</From><To>EUR</To><Amount>100.00</Amount></XML>"
        }
    }

    def to_xml(self) -> str:
        root = Element("XML")

        from_elem = Element("From")
        from_elem.text = self.From
        root.append(from_elem)

        to_elem = Element("To")
        to_elem.text = self.To
        root.append(to_elem)

        amount_elem = Element("Amount")
        amount_elem.text = str(self.Amount)
        root.append(amount_elem)

        return tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_string: str) -> 'API2Request':
        root = ET.fromstring(xml_string)
        return cls(
            From=root.find('From').text,
            To=root.find('To').text,
            Amount=Decimal(root.find('Amount').text)
        )


class API2Response(BaseModel):
    Result: Decimal = Field(..., description="Converted amount")

    model_config = {
        "json_schema_extra": {
            "example": {
                "Result": 85.00
            },
            "description": "Actual response will be in XML format: <XML><Result>85.00</Result></XML>"
        }
    }

    def to_xml(self) -> str:
        root = Element("XML")
        result_elem = Element("Result")
        result_elem.text = str(self.Result)
        root.append(result_elem)
        return tostring(root, encoding='unicode')

    @classmethod
    def from_xml(cls, xml_string: str) -> 'API2Response':
        root = ET.fromstring(xml_string)
        return cls(Result=Decimal(root.find('Result').text))


class API3ExchangeData(BaseModel):
    sourceCurrency: str = Field(..., description="Source currency", min_length=3, max_length=3)
    targetCurrency: str = Field(..., description="Target currency", min_length=3, max_length=3)
    quantity: Decimal = Field(..., description="Amount to convert", gt=0)


class API3Request(BaseModel):
    exchange: API3ExchangeData = Field(..., description="Exchange details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "exchange": {
                    "sourceCurrency": "USD",
                    "targetCurrency": "EUR",
                    "quantity": 100.00
                }
            }
        }
    }


class API3DataResponse(BaseModel):
    total: Decimal = Field(..., description="Total converted amount")


class API3Response(BaseModel):
    statusCode: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")
    data: API3DataResponse = Field(..., description="Response data")

    model_config = {
        "json_schema_extra": {
            "example": {
                "statusCode": 200,
                "message": "Exchange completed successfully",
                "data": {
                    "total": 86.50
                }
            }
        }
    }
