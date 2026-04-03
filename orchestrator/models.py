from sqlalchemy import Column, Integer, String, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, engine, SessionLocal
from common.schemas import JobStatus, StepStatus

class JobRecord(Base):
    __tablename__ = "jobs"
    id = Column(String(50), primary_key=True, index=True)
    user_input = Column(String(255))
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    steps = relationship("StepRecord", back_populates="job")

class StepRecord(Base):
    __tablename__ = "steps"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), ForeignKey("jobs.id"))
    step_id = Column(String(50))
    service = Column(String(50))
    action = Column(String(50))
    params = Column(JSON)
    undo_action = Column(String(50), nullable=True)
    undo_params = Column(JSON, nullable=True)
    status = Column(SQLEnum(StepStatus), default=StepStatus.PENDING)
    
    job = relationship("JobRecord", back_populates="steps")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
