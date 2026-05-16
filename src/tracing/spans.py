"""Span data models."""

from pydantic import BaseModel, Field
from datetime import datetime, UTC


class SpanRecord(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    name: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None
    latency_ms: float | None = None
    status: str = "success"
    error: str | None = None
