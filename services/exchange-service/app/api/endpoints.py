import os
import sys

from fastapi import APIRouter, HTTPException

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from common.services.exchange_service import ExchangeService
from common.models.request import ExchangeRequest
from common.models.response import BestExchangeResponse
from common.utils.logger import setup_logger

router = APIRouter()
exchange_service = ExchangeService()
logger = setup_logger("Exchange_Service_Endpoints")


@router.get("/")
async def root():
    return {
        "message": "RateCompare Exchange Compare Service",
        "version": "1.0.0",
        "description": "Compares exchange rates from multiple providers and returns the best offer",
        "endpoint": "POST /exchange/compare",
        "input_format": {"source_currency": "string", "target_currency": "string", "amount": "number"}
    }


@router.post("/exchange/compare")
async def compare_exchange_rates(request: ExchangeRequest) -> BestExchangeResponse:
    try:
        logger.info(
            f"Exchange compare request: {request.source_currency} -> {request.target_currency}, amount: {request.amount}")
        response = await exchange_service.get_best_exchange_rate(request)
        logger.info(f"Exchange compare completed successfully. Best rate from {response.data.bestOffer.provider}")
        return response
    except Exception as e:
        logger.error(f"Exchange compare error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Exchange Compare"}
