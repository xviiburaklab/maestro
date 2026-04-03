from fastapi import FastAPI
from common.logging_utils import setup_logging
from common.middleware import CorrelationIdMiddleware
from common.observability import instrument_app

logger = setup_logging("notification-service")
app = FastAPI(title="Notification Service")
app.add_middleware(CorrelationIdMiddleware)
instrument_app(app, "notification-service")

@app.post("/send")
async def send_notification(data: dict):
    logger.info(f"Sending notification: {data}")
    return {"status": "sent"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
