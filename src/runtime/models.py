from datetime import datetime,timezone
from enum import StrEnum
from pydantic import BaseModel,Field

class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchRun(BaseModel):
    run_id: str
    thread_id: str
    query: str
    status:RunStatus=RunStatus.PENDING
    result: str | None = None
    error: str | None = None
    created_at:datetime=Field(
        default_factory=lambda:datetime.now(timezone.utc)
    )
    started_at: datetime | None = None
    completed_at: datetime | None = None