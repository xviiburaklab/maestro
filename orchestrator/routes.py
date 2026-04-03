from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from .models import JobRecord, StepRecord, get_db
from .planner import LocalHeuristicPlanner
from common.schemas import OrchestrationPlan, JobStatus, StepStatus
import uuid
import os
from common.events import publisher

router = APIRouter()
planner = LocalHeuristicPlanner()

@router.post("/orchestrate", response_model=OrchestrationPlan)
async def orchestrate(user_input: str = Body(..., embed=True), db: Session = Depends(get_db)):
    steps = await planner.plan(user_input, {})
    job_id = str(uuid.uuid4())
    
    # Init workflow state machine state
    job_rec = JobRecord(id=job_id, user_input=user_input, status=JobStatus.PENDING)
    db.add(job_rec)
    
    for step in steps:
        step_rec = StepRecord(
            job_id=job_id,
            step_id=step.step_id,
            service=step.service,
            action=step.action,
            params=step.params,
            undo_action=step.undo_action,
            undo_params=step.undo_params,
            status=StepStatus.PENDING
        )
        db.add(step_rec)
    
    db.commit()
    
    publisher.publish("workflow.execute", {"job_id": job_id})
    
    return OrchestrationPlan(job_id=job_id, user_input=user_input, steps=steps)

@router.get("/executions/{job_id}", response_model=OrchestrationPlan)
def get_execution_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        return {"error": "Job not found"}
    
    return OrchestrationPlan(
        job_id=job.id,
        user_input=job.user_input,
        status=job.status,
        steps=[
            {
                "step_id": s.step_id,
                "service": s.service,
                "action": s.action,
                "status": s.status,
                "params": s.params
            } for s in job.steps
        ]
    )
