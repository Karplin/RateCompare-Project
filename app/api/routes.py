from fastapi import APIRouter, HTTPException
from app.models.request import ExchangeRequest
from app.models.response import BestExchangeResponse
from app.services.exchange_service import ExchangeService
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)
exchange_service = ExchangeService()


@router.get("/")
async def root():
    return {"message": "RateCompare API - Banking Exchange Rate Comparison Service"}


@router.post("/exchange", response_model=BestExchangeResponse)
async def get_exchange_rate(request: ExchangeRequest):
    try:
        logger.info(f"Received exchange request: {request}")
        result = await exchange_service.get_best_exchange_rate(request)
        logger.info(
            f"Exchange completed successfully. Best rate: {result.best_offer.rate} from {result.best_offer.provider}")
        return result
    except Exception as e:
        logger.error(f"Error processing exchange request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "RateCompare Exchange API"
    }
