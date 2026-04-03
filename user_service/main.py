from fastapi import FastAPI
from common.logging_utils import setup_logging
from common.middleware import CorrelationIdMiddleware
from user_service.routes import router as user_router
from common.observability import instrument_app

logger = setup_logging("user-service")
app = FastAPI(title="User Service")
app.add_middleware(CorrelationIdMiddleware)
instrument_app(app, "user-service")

app.include_router(user_router, prefix="/users", tags=["Users"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
