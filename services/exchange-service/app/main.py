from fastapi import FastAPI

from api.endpoints import router

app = FastAPI(
    title="RateCompare Exchange Compare Service",
    description="Exchange Rate Comparison Service - Compares rates from multiple APIs and selects the best deal",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
