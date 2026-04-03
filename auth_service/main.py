from fastapi import FastAPI
from common.logging_utils import setup_logging
from common.middleware import CorrelationIdMiddleware
from auth_service.routes import router as auth_router
from common.observability import instrument_app

logger = setup_logging("auth-service")
app = FastAPI(title="Auth Service")
app.add_middleware(CorrelationIdMiddleware)
instrument_app(app, "auth-service")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
