"""Trace context propagation via contextvars."""

from contextvars import ContextVar

current_trace_id: ContextVar[str | None] = ContextVar("current_trace_id", default=None)
current_span_id: ContextVar[str | None] = ContextVar("current_span_id", default=None)
