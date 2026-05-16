"""Core tracer interface."""

from datetime import datetime, UTC
from src.tracing.context import current_trace_id, current_span_id
from src.tracing.spans import SpanRecord
from src.utils.ids import make_trace_id, make_span_id


class Tracer:
    def start_trace(self) -> tuple[str, str]:
        trace_id = make_trace_id()
        span_id = make_span_id()
        current_trace_id.set(trace_id)
        current_span_id.set(span_id)
        return trace_id, span_id

    def start_span(self, name: str, parent_span_id: str | None = None) -> SpanRecord:
        trace_id = current_trace_id.get() or make_trace_id()
        span_id = make_span_id()
        current_trace_id.set(trace_id)
        current_span_id.set(span_id)
        return SpanRecord(trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id, name=name)

    def end_span(self, span: SpanRecord, latency_ms: float, status: str = "success", error: str | None = None) -> SpanRecord:
        span.ended_at = datetime.now(UTC)
        span.latency_ms = latency_ms
        span.status = status
        span.error = error
        return span


tracer = Tracer()
