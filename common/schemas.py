from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    WORKER = "worker"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATED = "compensated"

class StepStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

class ExecutionStep(BaseModel):
    step_id: str
    service: str
    action: str
    params: dict
    undo_action: Optional[str] = None
    undo_params: Optional[dict] = None
    status: StepStatus = StepStatus.PENDING

class OrchestrationPlan(BaseModel):
    job_id: str
    user_input: str
    steps: List[ExecutionStep]
    status: JobStatus = JobStatus.PENDING

class AuditLog(BaseModel):
    id: Optional[str] = None
    correlation_id: str
    service: str
    event: str
    details: Any
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
