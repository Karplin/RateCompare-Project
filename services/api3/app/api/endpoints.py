import os
import sys

from fastapi import APIRouter, HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from common.providers.api3_provider import API3DirectProvider
from common.models.api_formats import API3Request, API3Response
from common.utils.logger import setup_logger

router = APIRouter()
provider = API3DirectProvider()
logger = setup_logger("API3_Endpoints")


@router.get("/")
async def root():
    return {
        "message": "RateCompare API3 - Nested JSON Provider",
        "version": "1.0.0",
        "description": "Nested JSON format exchange rate service",
        "endpoint": "POST /exchange/rate",
        "input_format": {"exchange": {"sourceCurrency": "string", "targetCurrency": "string", "quantity": "number"}},
        "output_format": {"statusCode": "number", "message": "string", "data": {"total": "number"}}
    }


@router.post("/exchange/rate")
async def get_exchange_rate(request: API3Request) -> API3Response:
    try:
        logger.info(
            f"API3 request received: {request.exchange.sourceCurrency} -> {request.exchange.targetCurrency}, amount: {request.exchange.quantity}")
        response = await provider.get_exchange_rate(request)
        logger.info(f"API3 response: total {response.data.total}")
        return response
    except ValueError as e:
        logger.error(f"API3 error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API3 unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API3"}
