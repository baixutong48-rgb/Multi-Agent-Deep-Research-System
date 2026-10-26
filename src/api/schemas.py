from pydantic import BaseModel, Field

from src.runtime.models import RunStatus

class ResearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=20_000,
    )

class ResearchCreatedResponse(BaseModel):
    run_id: str
    status: RunStatus

class ResearchStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    result: str | None = None
    error: str | None = None