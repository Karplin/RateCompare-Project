from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="RateCompare API",
    description="Banking Exchange Rate Comparison Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
