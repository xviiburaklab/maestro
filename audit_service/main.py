from fastapi import FastAPI
from common.logging_utils import setup_logging
from common.middleware import CorrelationIdMiddleware
from audit_service.routes import router as audit_router
from audit_service.database import setup_db
from common.observability import instrument_app

logger = setup_logging("audit-service")
app = FastAPI(title="Audit Service")
app.add_middleware(CorrelationIdMiddleware)
instrument_app(app, "audit-service")

@app.on_event("startup")
async def startup_event():
    await setup_db()

app.include_router(audit_router, prefix="/audit", tags=["Audit"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
