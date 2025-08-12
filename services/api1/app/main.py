from fastapi import FastAPI

from .api.endpoints import router

app = FastAPI(
    title="RateCompare API1 - JSON Provider",
    description="API1 Provider - JSON format exchange rate service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
