from fastapi import APIRouter, HTTPException

from app.models.request import ExchangeRequest, VALID_CURRENCIES
from app.models.response import BestExchangeResponse, ExchangeResponse
from app.providers.api1_provider import API1Provider
from app.providers.api2_provider import API2Provider
from app.providers.api3_provider import API3Provider
from app.services.exchange_service import ExchangeService
from app.utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

exchange_service = ExchangeService()
api1_provider = API1Provider()
api2_provider = API2Provider()
api3_provider = API3Provider()


@router.get("/")
async def root():
    return {
        "message": "RateCompare API - Banking Exchange Rate Comparison Service",
        "version": "1.0.0",
        "endpoints": {
            "compare_all": "POST /exchange/compare",
            "individual_apis": [
                "POST /exchange/rate/api1",
                "POST /exchange/rate/api2",
                "POST /exchange/rate/api3"
            ]
        }
    }


@router.post("/exchange/compare", response_model=BestExchangeResponse)
async def get_exchange_rate(request: ExchangeRequest):
    try:
        logger.info(f"Received exchange request: {request}")
        result = await exchange_service.get_best_exchange_rate(request)
        logger.info(
            f"Exchange completed successfully. Best rate: {result.best_offer.rate} from {result.best_offer.provider}")
        return result
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Validation Error",
            "message": str(e),
            "supported_currencies": sorted(list(VALID_CURRENCIES))
        })
    except Exception as e:
        logger.error(f"Error processing exchange request: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "Internal Server Error",
            "message": str(e)
        })


@router.post("/exchange/rate/api1", response_model=ExchangeResponse)
async def get_api1_rate(request: ExchangeRequest):
    try:
        logger.info(f"API1 request: {request}")
        result = await api1_provider.get_exchange_rate(request)
        if result:
            logger.info(f"API1 completed successfully. Rate: {result.rate}")
            return result
        else:
            raise HTTPException(status_code=503, detail={
                "error": "Service Unavailable",
                "message": "API1 provider is currently unavailable"
            })
    except ValueError as e:
        logger.warning(f"API1 validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Validation Error",
            "message": str(e),
            "provider": "API1",
            "supported_currencies": sorted(list(VALID_CURRENCIES))
        })
    except Exception as e:
        logger.error(f"Error with API1 provider: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "API1 Provider Error",
            "message": str(e)
        })


@router.post("/exchange/rate/api2", response_model=ExchangeResponse)
async def get_api2_rate(request: ExchangeRequest):
    try:
        logger.info(f"API2 request: {request}")
        result = await api2_provider.get_exchange_rate(request)
        if result:
            logger.info(f"API2 completed successfully. Rate: {result.rate}")
            return result
        else:
            raise HTTPException(status_code=503, detail={
                "error": "Service Unavailable",
                "message": "API2 provider is currently unavailable"
            })
    except ValueError as e:
        logger.warning(f"API2 validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Validation Error",
            "message": str(e),
            "provider": "API2",
            "supported_currencies": sorted(list(VALID_CURRENCIES))
        })
    except Exception as e:
        logger.error(f"Error with API2 provider: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "API2 Provider Error",
            "message": str(e)
        })


@router.post("/exchange/rate/api3", response_model=ExchangeResponse)
async def get_api3_rate(request: ExchangeRequest):
    try:
        logger.info(f"API3 request: {request}")
        result = await api3_provider.get_exchange_rate(request)
        if result:
            logger.info(f"API3 completed successfully. Rate: {result.rate}")
            return result
        else:
            raise HTTPException(status_code=503, detail={
                "error": "Service Unavailable",
                "message": "API3 provider is currently unavailable"
            })
    except ValueError as e:
        logger.warning(f"API3 validation error: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Validation Error",
            "message": str(e),
            "provider": "API3",
            "supported_currencies": sorted(list(VALID_CURRENCIES))
        })
    except Exception as e:
        logger.error(f"Error with API3 provider: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "error": "API3 Provider Error",
            "message": str(e)
        })
