from fastapi import FastAPI
from common.logging_utils import setup_logging
from common.middleware import CorrelationIdMiddleware
from orchestrator.routes import router as orchestrator_router
from common.observability import instrument_app

logger = setup_logging("orchestrator")
app = FastAPI(title="Orchestrator Service")
app.add_middleware(CorrelationIdMiddleware)
instrument_app(app, "orchestrator")

app.include_router(orchestrator_router, prefix="/api", tags=["Orchestration"])

@app.get("/health")
async def health():
    return {"status": "healthy"}
