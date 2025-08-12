import os
import sys

from fastapi import APIRouter, HTTPException, Request, Response

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from common.providers.api2_provider import API2DirectProvider
from common.models.api_formats import API2Request
from common.utils.logger import setup_logger

router = APIRouter()
provider = API2DirectProvider()
logger = setup_logger("API2_Endpoints")


@router.get("/")
async def root():
    return {
        "message": "RateCompare API2 - XML Provider",
        "version": "1.0.0",
        "description": "XML format exchange rate service",
        "endpoint": "POST /exchange/rate",
        "input_format": "<XML><From>string</From><To>string</To><Amount>number</Amount></XML>",
        "output_format": "<XML><Result>number</Result></XML>",
        "content_type": "application/xml"
    }


@router.post("/exchange/rate")
async def get_exchange_rate_xml(request: Request):
    try:
        xml_content = await request.body()
        xml_text = xml_content.decode('utf-8')

        logger.info(f"API2 XML request received: {xml_text}")

        api2_request = API2Request.from_xml(xml_text)

        response = await provider.get_exchange_rate(api2_request)

        xml_response = response.to_xml()

        logger.info(f"API2 XML response: {xml_response}")

        return Response(
            content=xml_response,
            media_type="application/xml"
        )

    except ValueError as e:
        logger.error(f"API2 error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API2 unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API2"}
