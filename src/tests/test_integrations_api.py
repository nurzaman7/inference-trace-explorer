from fastapi.testclient import TestClient

from src import api as api_module


def test_ingest_trace_endpoint():
    client = TestClient(api_module.app)
    payload = {
        "trace_id": "tid-1",
        "span_id": "sid-1",
        "timestamp": "2026-05-16T12:00:00Z",
        "input": "hello",
        "output": "world",
        "latency_ms": 12.5,
        "tokens_in": 2,
        "tokens_out": 3,
        "memory_mb": 256.0,
        "status": "success",
        "provider": "custom-agent",
        "model": "router",
        "metadata": {"job": "test"},
    }
    res = client.post("/ingest/trace", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ingested"
    assert data["trace_id"] == "tid-1"


def test_openai_integration_endpoint_with_mock(monkeypatch):
    def fake_call_openai_compatible(**kwargs):
        return {
            "trace_id": "t-openai",
            "span_id": "s-openai",
            "timestamp": "2026-05-16T12:00:00Z",
            "input": "prompt",
            "output": "answer",
            "latency_ms": 42.0,
            "tokens_in": 11,
            "tokens_out": 7,
            "memory_mb": 123.0,
            "status": "success",
            "error": None,
            "provider": "openai-compatible",
            "model": kwargs["model"],
            "metadata": kwargs.get("metadata", {}),
            "provider_response": {"usage": {"prompt_tokens": 11, "completion_tokens": 7}},
        }

    monkeypatch.setattr(api_module.integration_service, "call_openai_compatible", fake_call_openai_compatible)
    client = TestClient(api_module.app)

    res = client.post(
        "/integrations/openai/chat",
        json={
            "api_key": "dummy",
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "hello"}],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "openai-compatible"
    assert data["tokens_in"] == 11
    assert data["tokens_out"] == 7


def test_anthropic_integration_endpoint_with_mock(monkeypatch):
    def fake_call_anthropic(**kwargs):
        return {
            "trace_id": "t-anth",
            "span_id": "s-anth",
            "timestamp": "2026-05-16T12:00:00Z",
            "input": "prompt",
            "output": "answer",
            "latency_ms": 35.0,
            "tokens_in": 19,
            "tokens_out": 13,
            "memory_mb": 111.0,
            "status": "success",
            "error": None,
            "provider": "anthropic",
            "model": kwargs["model"],
            "metadata": kwargs.get("metadata", {}),
            "provider_response": {"usage": {"input_tokens": 19, "output_tokens": 13}},
        }

    monkeypatch.setattr(api_module.integration_service, "call_anthropic", fake_call_anthropic)
    client = TestClient(api_module.app)

    res = client.post(
        "/integrations/anthropic/messages",
        json={
            "api_key": "dummy",
            "model": "claude-3-5-sonnet-latest",
            "messages": [{"role": "user", "content": "hello"}],
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["provider"] == "anthropic"
    assert data["tokens_in"] == 19
    assert data["tokens_out"] == 13
