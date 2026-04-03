import os
import requests
import time
from orchestrator.models import SessionLocal, JobRecord, StepRecord
from common.schemas import JobStatus, StepStatus
import logging

logger = logging.getLogger("worker")

def update_step_status(step_id: int, status: StepStatus):
    db = SessionLocal()
    step = db.query(StepRecord).filter(StepRecord.id == step_id).first()
    if step:
        step.status = status
        db.commit()
    db.close()

def update_job_status(job_id: str, status: JobStatus):
    db = SessionLocal()
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if job:
        job.status = status
        db.commit()
    db.close()

def execute_workflow(data: dict):
    job_id = data.get("job_id")
    if not job_id:
        return "No job_id provided"
    
    db = SessionLocal()
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    if not job:
        return "Job not found"
    
    update_job_status(job_id, JobStatus.IN_PROGRESS)
    
    steps = db.query(StepRecord).filter(StepRecord.job_id == job_id).order_by(StepRecord.id).all()
    
    for step in steps:
        success = execute_step(step.id)
        if not success:
            trigger_compensation(job_id)
            return f"Job {job_id} failed at step {step.step_id}"
    
    update_job_status(job_id, JobStatus.COMPLETED)
    return f"Job {job_id} completed successfully"

def execute_step(step_db_id: int):
    db = SessionLocal()
    step = db.query(StepRecord).filter(StepRecord.id == step_db_id).first()
    
    update_step_status(step_db_id, StepStatus.PENDING)
    
    try:
        logger.info(f"Executing {step.action} on {step.service} with params {step.params}")
        
        # Test saga workflow execution failure
        if step.action == "assign_role" and "fail" in step.params.get("username", ""):
            raise Exception("Simulated Role Assignment Failure")
            
        time.sleep(1) # Network latency
        update_step_status(step_db_id, StepStatus.SUCCESS)
        return True
    except Exception as e:
        logger.error(f"Step {step.step_id} failed: {str(e)}")
        update_step_status(step_db_id, StepStatus.FAILURE)
        return False
    finally:
        db.close()

def trigger_compensation(job_id: str):
    db = SessionLocal()
    job = db.query(JobRecord).filter(JobRecord.id == job_id).first()
    update_job_status(job_id, JobStatus.FAILED)
    
    # Run undo actions for completed steps in reverse order
    steps = db.query(StepRecord).filter(
        StepRecord.job_id == job_id, 
        StepRecord.status == StepStatus.SUCCESS
    ).order_by(StepRecord.id.desc()).all()
    
    for step in steps:
        if step.undo_action:
            logger.info(f"Compensating: Undoing {step.action} using {step.undo_action}")
            update_step_status(step.id, StepStatus.COMPENSATING)
            time.sleep(1)
            update_step_status(step.id, StepStatus.COMPENSATED)
    
    update_job_status(job_id, JobStatus.COMPENSATED)
    db.close()
