import os
import sys

from fastapi import APIRouter, HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from common.providers.api1_provider import API1DirectProvider
from common.models.api_formats import API1Request, API1Response
from common.utils.logger import setup_logger

router = APIRouter()
provider = API1DirectProvider()
logger = setup_logger("API1_Endpoints")


@router.get("/")
async def root():
    return {
        "message": "RateCompare API1 - JSON Provider",
        "version": "1.0.0",
        "description": "JSON format exchange rate service",
        "endpoint": "POST /exchange/rate",
        "input_format": {"from": "string", "to": "string", "value": "number"},
        "output_format": {"rate": "number"}
    }


@router.post("/exchange/rate")
async def get_exchange_rate(request: API1Request) -> API1Response:
    try:
        logger.info(f"API1 request received: {request.from_} -> {request.to}, amount: {request.value}")
        response = await provider.get_exchange_rate(request)
        logger.info(f"API1 response: rate {response.rate}")
        return response
    except ValueError as e:
        logger.error(f"API1 error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API1 unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API1"}
