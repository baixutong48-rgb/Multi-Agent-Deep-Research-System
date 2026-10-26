from datetime import datetime,timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel,Field
from uuid import uuid4

class TraceEventType(StrEnum):
    RUN_STARTED = "run_started"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"

    DELEGATION_STARTED = "delegation_started"
    DELEGATION_COMPLETED = "delegation_completed"

    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"

    ARTIFACT_CREATED = "artifact_created"

class TraceEvent(BaseModel):
    event_id : str = Field(
        default_factory=lambda:f'evt_{uuid4().hex}'
    )
    run_id:str
    sequence: int
    event_type: TraceEventType
    timestamp: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc)
    )
    actor: str | None = None

    name: str | None = None

    metadata: dict[str,Any] = Field(
        default_factory=dict
    )