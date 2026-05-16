from fastapi.testclient import TestClient

from src import api as api_module
from src.instrumentation.otel_adapter import trace_record_to_otel_span


def test_trace_record_to_otel_span_shape():
    span = trace_record_to_otel_span(
        {
            "trace_id": "t1",
            "span_id": "s1",
            "timestamp": "2026-05-16T00:00:00Z",
            "latency_ms": 10.5,
            "tokens_in": 2,
            "tokens_out": 3,
            "memory_mb": 100,
            "status": "success",
        }
    )
    assert span["trace_id"] == "t1"
    assert "start_time_unix_nano" in span
    assert "attributes" in span


def test_otel_spans_endpoint():
    client = TestClient(api_module.app)
    res = client.get("/otel/spans", params={"limit": 5})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
