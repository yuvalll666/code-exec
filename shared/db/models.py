from sqlalchemy import Column, String, Text, DateTime, Enum
from .database import Base
from datetime import datetime, timezone
import enum

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class CodeJob(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    code = Column(Text, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))