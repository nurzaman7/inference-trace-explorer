"""ID utilities for trace/span generation."""

from uuid import uuid4


def make_trace_id() -> str:
    return uuid4().hex


def make_span_id() -> str:
    return uuid4().hex[:16]
