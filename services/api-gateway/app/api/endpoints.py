import os
import sys

from fastapi import APIRouter, HTTPException, Request, Response

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from common.models.api_formats import (
    API1Request, API1Response,
    API2Request, API3Request, API3Response
)
from common.models.request import ExchangeRequest, VALID_CURRENCIES
from common.models.response import BestExchangeResponse
from common.providers.api1_provider import API1DirectProvider
from common.providers.api2_provider import API2DirectProvider
from common.providers.api3_provider import API3DirectProvider
from common.services.exchange_service import ExchangeService
from common.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

exchange_service = ExchangeService()
api1_direct_provider = API1DirectProvider()
api2_direct_provider = API2DirectProvider()
api3_direct_provider = API3DirectProvider()


@router.get("/",
            tags=["API EXCHANGE"],
            summary="API Documentation and Service Info",
            description="Returns service information and available endpoints")
async def root():
    return {
        "message": "RateCompare API - Banking Exchange Rate Comparison Service",
        "version": "1.0.0",
        "endpoints": {
            "compare_all": {
                "url": "POST /exchange/compare",
                "format": "Unified format: {source_currency, target_currency, amount}"
            },
            "individual_apis": [
                {
                    "name": "API1 (JSON)",
                    "url": "POST /exchange/rate/api1",
                    "input": "{from, to, value}",
                    "output": "{rate}"
                },
                {
                    "name": "API2 (XML)",
                    "url": "POST /exchange/rate/api2",
                    "input": "<XML><From>USD</From><To>EUR</To><Amount>100.00</Amount></XML>",
                    "output": "<XML><Result>85.00</Result></XML>",
                    "content_type": "application/xml",
                    "note": "Native XML API - sends and receives actual XML"
                },
                {
                    "name": "API3 (Nested JSON)",
                    "url": "POST /exchange/rate/api3",
                    "input": "{exchange: {sourceCurrency, targetCurrency, quantity}}",
                    "output": "{statusCode, message, data: {total}}"
                }
            ]
        }
    }


@router.post("/exchange/compare",
             response_model=BestExchangeResponse,
             tags=["API EXCHANGE"],
             summary="Compare exchange rates from all APIs",
             description="Compares rates from API1, API2, and API3 and returns the best offer")
async def get_exchange_rate(request: ExchangeRequest):
    try:
        logger.info(f"Received exchange request: {request}")

        result = await exchange_service.get_best_exchange_rate(request)

        logger.info(
            f"Exchange completed successfully. Best rate: {result.data.bestOffer.rate} from {result.data.bestOffer.provider}")
        return result

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "statusCode": 400,
            "message": str(e),
            "data": {
                "error": "Validation Error",
                "supported_currencies": sorted(list(VALID_CURRENCIES))
            }
        })
    except Exception as e:
        logger.error(f"Error processing exchange request: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "statusCode": 500,
            "message": "Internal server error occurred during exchange comparison",
            "data": {
                "error": "Internal Server Error",
                "details": str(e)
            }
        })


@router.post("/exchange/rate/api1",
             response_model=API1Response,
             tags=["API1 (JSON)"],
             summary="Get exchange rate from API1",
             description="API1 JSON Format: Input {from, to, value} → Output {rate}")
async def get_api1_rate(request: API1Request):
    try:
        logger.info(f"API1 request: {request}")

        result = await api1_direct_provider.get_exchange_rate(request)

        logger.info(f"API1 completed successfully. Rate: {result.rate}")

        return result

    except ValueError as e:
        logger.warning(f"API1 validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Validation Error",
            "message": str(e),
            "provider": "API1",
            "expected_format": {
                "from": "string (3 chars)",
                "to": "string (3 chars)",
                "value": "decimal > 0"
            }
        })
    except Exception as e:
        logger.error(f"Error with API1 provider: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "API1 Provider Error",
            "message": str(e)
        })


@router.post("/exchange/rate/api2",
             response_class=Response,
             tags=["API2 (XML)"],
             summary="Get exchange rate from API2",
             description="API2 XML Format: Input <XML><From/><To/><Amount/></XML> → Output <XML><Result/></XML>",
             responses={
                 200: {
                     "description": "Successful XML response",
                     "content": {"application/xml": {"example": "<XML><Result>85.00</Result></XML>"}}
                 },
                 400: {"description": "Invalid XML format or validation error"},
                 500: {"description": "Internal server error"}
             })
async def get_api2_rate(request: Request):
    try:
        xml_body = await request.body()
        xml_string = xml_body.decode('utf-8')

        logger.info(f"API2 XML request: {xml_string}")

        api2_request = API2Request.from_xml(xml_string)

        result = await api2_direct_provider.get_exchange_rate(api2_request)

        xml_response = result.to_xml()

        logger.info(f"API2 completed successfully. XML Result: {xml_response}")

        return Response(
            content=xml_response,
            media_type="application/xml",
            status_code=200
        )

    except ValueError as e:
        logger.warning(f"API2 validation error: {str(e)}")

        error_xml = f"""<XML><Error>
            <Code>ValidationError</Code>
            <Message>{str(e)}</Message>
            <ExpectedFormat>&lt;XML&gt;&lt;From&gt;USD&lt;/From&gt;&lt;To&gt;EUR&lt;/To&gt;&lt;Amount&gt;100.00&lt;/Amount&gt;&lt;/XML&gt;</ExpectedFormat>
        </Error></XML>"""

        return Response(content=error_xml, media_type="application/xml", status_code=400)

    except Exception as e:
        logger.error(f"Error with API2 provider: {str(e)}")
        error_xml = f"""<XML><Error>
            <Code>InternalError</Code>
            <Message>{str(e)}</Message>
        </Error></XML>"""
        return Response(content=error_xml, media_type="application/xml", status_code=500)


@router.post("/exchange/rate/api3",
             response_model=API3Response,
             tags=["API3 (JSON)"],
             summary="Get exchange rate from API3",
             description="API3 Nested JSON Format: Input {exchange: {sourceCurrency, targetCurrency, quantity}} → Output {statusCode, message, data: {total}}")
async def get_api3_rate(request: API3Request):
    try:
        logger.info(f"API3 request: {request}")

        result = await api3_direct_provider.get_exchange_rate(request)

        logger.info(f"API3 completed successfully. Total: {result.data.total}")

        return result

    except ValueError as e:
        logger.warning(f"API3 validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Validation Error",
            "message": str(e),
            "provider": "API3",
            "expected_format": {
                "exchange": {
                    "sourceCurrency": "string (3 chars)",
                    "targetCurrency": "string (3 chars)",
                    "quantity": "decimal > 0"
                }
            }
        })
    except Exception as e:
        logger.error(f"Error with API3 provider: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "API3 Provider Error",
            "message": str(e)
        })
