"""Event model for trace timeline."""

from pydantic import BaseModel, Field
from datetime import datetime, UTC


class TraceEvent(BaseModel):
    trace_id: str
    span_id: str
    event_type: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict = Field(default_factory=dict)
