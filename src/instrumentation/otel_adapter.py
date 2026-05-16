"""OpenTelemetry export adapter for trace records.

This module keeps OpenTelemetry optional. If OTEL packages are unavailable,
it still returns OTEL-like JSON span payloads for debugging/export.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _iso_to_unix_nanos(value: str) -> int:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


def trace_record_to_otel_span(record: dict[str, Any], service_name: str = "inference-trace-explorer") -> dict[str, Any]:
    start_ns = _iso_to_unix_nanos(record.get("timestamp", datetime.now(timezone.utc).isoformat()))
    latency_ms = float(record.get("latency_ms", 0.0) or 0.0)
    end_ns = start_ns + int(latency_ms * 1_000_000)

    attrs = {
        "service.name": service_name,
        "llm.provider": str(record.get("provider", "unknown")),
        "llm.model": str(record.get("model", "unknown")),
        "llm.tokens.in": int(record.get("tokens_in", 0) or 0),
        "llm.tokens.out": int(record.get("tokens_out", 0) or 0),
        "llm.memory.mb": float(record.get("memory_mb", 0.0) or 0.0),
        "trace.status": str(record.get("status", "unknown")),
    }
    if record.get("error"):
        attrs["exception.message"] = str(record.get("error"))

    return {
        "trace_id": str(record.get("trace_id", "")),
        "span_id": str(record.get("span_id", "")),
        "parent_span_id": str(record.get("parent_span_id", "")) or None,
        "name": "llm.inference",
        "start_time_unix_nano": start_ns,
        "end_time_unix_nano": end_ns,
        "attributes": attrs,
    }


def export_otel_like_json(records: list[dict[str, Any]], service_name: str = "inference-trace-explorer") -> list[dict[str, Any]]:
    return [trace_record_to_otel_span(r, service_name=service_name) for r in records]
