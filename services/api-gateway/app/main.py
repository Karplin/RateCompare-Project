from fastapi import FastAPI

from .api.endpoints import router

app = FastAPI(
    title="RateCompare API",
    description="Banking Exchange Rate Comparison Service - Compares rates from multiple APIs and selects the best deal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "API EXCHANGE",
            "description": "Main comparison endpoint that queries all providers and returns the best rate"
        },
        {
            "name": "API1 (JSON)",
            "description": "Access to API1 provider - JSON format"
        },
        {
            "name": "API2 (XML)",
            "description": "Access to API2 provider - XML format"
        },
        {
            "name": "API3 (JSON)",
            "description": "Access to API3 provider - Nested JSON format"
        }
    ]
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000"))
    )
