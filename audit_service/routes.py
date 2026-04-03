from fastapi import APIRouter, Body
from .database import logs_collection
from common.schemas import AuditLog
from typing import List

router = APIRouter()

@router.post("/log")
async def create_log(log: AuditLog = Body(...)):
    await logs_collection.insert_one(log.dict())
    return {"status": "logged"}

@router.get("/correlation/{correlation_id}", response_model=List[AuditLog])
async def get_logs_by_correlation(correlation_id: str):
    cursor = logs_collection.find({"correlation_id": correlation_id})
    logs = await cursor.to_list(length=100)
    for log in logs:
        log["id"] = str(log.pop("_id"))
    return logs
