"""FastAPI service exposing inference tracing and integration APIs."""

from __future__ import annotations

from io import StringIO
from random import random
from threading import Lock
from time import perf_counter

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
import pandas as pd

from src.instrumentation.middleware import TraceMiddleware
from src.models.inference_engine import InferenceEngine
from src.storage.sqlite_store import SQLiteStore
from src.storage.jsonl_store import JSONLStore
from src.storage.query_engine import QueryEngine
from src.storage.async_writer import AsyncTraceWriter
from src.analytics.latency_analysis import latency_percentiles
from src.analytics.error_analysis import error_rate
from src.analytics.token_analysis import token_totals
from src.analytics.anomaly_detection import latency_anomalies
from src.analytics.rollups import AnalyticsRollupWorker
from src.utils.config import settings
from src.api_models import (
    InferRequest,
    OpenAICompatibleRequest,
    AnthropicRequest,
    ExternalTraceRecord,
    BulkIngestRequest,
)
from src.integrations.service import IntegrationService
from src.loadgen import generate_trace_batch
from src.instrumentation.otel_adapter import export_otel_like_json


app = FastAPI(title="Inference Trace Explorer API", version="0.6.0")
app.add_middleware(TraceMiddleware)

engine = InferenceEngine()
integration_service = IntegrationService()
sqlite_store = SQLiteStore(settings.sqlite_path)
jsonl_store = JSONLStore(settings.jsonl_trace_path)
query_engine = QueryEngine(sqlite_store)
trace_writer = AsyncTraceWriter(sqlite_store=sqlite_store, jsonl_store=jsonl_store)
rollup_worker = AnalyticsRollupWorker(
    query_engine=query_engine,
    output_path=settings.analytics_rollup_path,
    interval_seconds=settings.rollup_interval_seconds,
)

_sampling_lock = Lock()
_sampling_seen = 0
_sampling_kept = 0
_sampling_dropped = 0


@app.on_event("startup")
def startup_event() -> None:
    trace_writer.start()
    rollup_worker.start()


@app.on_event("shutdown")
def shutdown_event() -> None:
    trace_writer.stop()
    rollup_worker.stop()


def _should_sample_keep() -> bool:
    rate = settings.trace_sample_rate
    if rate >= 1.0:
        return True
    if rate <= 0.0:
        return False
    return random() < rate


def _persist_record(record: dict) -> bool:
    global _sampling_seen, _sampling_kept, _sampling_dropped

    with _sampling_lock:
        _sampling_seen += 1

    if not _should_sample_keep():
        with _sampling_lock:
            _sampling_dropped += 1
        return False

    with _sampling_lock:
        _sampling_kept += 1

    if not trace_writer.enqueue(record):
        trace_writer.flush_sync(record)
    return True


def _sampling_metrics() -> dict:
    with _sampling_lock:
        return {
            "sample_rate": settings.trace_sample_rate,
            "seen_total": _sampling_seen,
            "kept_total": _sampling_kept,
            "dropped_total": _sampling_dropped,
        }


def _analytics_payload(limit: int) -> dict:
    rows = query_engine.recent_traces(limit=limit)
    df = pd.DataFrame(rows)
    if df.empty:
        return {
            "count": 0,
            "latency": {"p50": 0, "p95": 0, "p99": 0},
            "error_rate": 0,
            "tokens": {"tokens_in": 0, "tokens_out": 0},
            "anomalies": 0,
        }
    return {
        "count": len(df),
        "latency": latency_percentiles(df),
        "error_rate": error_rate(df),
        "tokens": token_totals(df),
        "anomalies": latency_anomalies(df),
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.env,
        "features": {
            "integrations": ["openai-compatible", "anthropic"],
            "storage": ["jsonl", "sqlite", "async-writer"],
            "rollups": True,
            "sampling": True,
        },
    }


@app.post("/infer")
def infer(payload: InferRequest) -> dict:
    record = engine.infer(payload.prompt)
    kept = _persist_record(record)
    record["sampled_in"] = kept
    return record


@app.post("/ingest/trace")
def ingest_trace(payload: ExternalTraceRecord) -> dict:
    record = payload.model_dump()
    kept = _persist_record(record)
    return {
        "status": "ingested" if kept else "sampled_out",
        "trace_id": record["trace_id"],
        "span_id": record["span_id"],
    }


@app.post("/ingest/bulk")
def ingest_bulk(payload: BulkIngestRequest) -> dict:
    started = perf_counter()
    batch = generate_trace_batch(payload.count, seed=payload.seed)
    accepted = 0
    sampled_out = 0

    for record in batch:
        if _persist_record(record):
            accepted += 1
        else:
            sampled_out += 1

    elapsed_ms = (perf_counter() - started) * 1000
    rate = accepted / (elapsed_ms / 1000) if elapsed_ms > 0 else 0.0

    return {
        "requested": payload.count,
        "accepted": accepted,
        "sampled_out": sampled_out,
        "enqueue_time_ms": round(elapsed_ms, 3),
        "enqueue_rate_per_sec": round(rate, 2),
    }


@app.post("/integrations/openai/chat")
def integration_openai_chat(payload: OpenAICompatibleRequest) -> dict:
    api_key = payload.api_key or settings.openai_api_key
    if not api_key:
        raise HTTPException(status_code=400, detail="Missing OpenAI API key. Provide api_key in request or set OPENAI_API_KEY in .env")

    base_url = payload.base_url or settings.openai_base_url
    record = integration_service.call_openai_compatible(
        api_key=api_key,
        base_url=base_url,
        model=payload.model,
        messages=[m.model_dump() for m in payload.messages],
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        metadata=payload.metadata,
    )
    kept = _persist_record(record)
    record["sampled_in"] = kept
    return record


@app.post("/integrations/anthropic/messages")
def integration_anthropic_messages(payload: AnthropicRequest) -> dict:
    api_key = payload.api_key or settings.anthropic_api_key
    if not api_key:
        raise HTTPException(status_code=400, detail="Missing Anthropic API key. Provide api_key in request or set ANTHROPIC_API_KEY in .env")

    base_url = payload.base_url or settings.anthropic_base_url
    record = integration_service.call_anthropic(
        api_key=api_key,
        base_url=base_url,
        model=payload.model,
        messages=[m.model_dump() for m in payload.messages],
        system=payload.system,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        metadata=payload.metadata,
    )
    kept = _persist_record(record)
    record["sampled_in"] = kept
    return record




@app.get("/otel/spans")
def otel_spans(limit: int = 200, service_name: str = "inference-trace-explorer") -> list[dict]:
    rows = query_engine.recent_traces(limit=limit)
    return export_otel_like_json(rows, service_name=service_name)

@app.get("/metrics/queue")
def queue_metrics() -> dict:
    return trace_writer.metrics()


@app.get("/metrics/sampling")
def sampling_metrics() -> dict:
    return _sampling_metrics()


@app.get("/traces")
def traces(limit: int = 100) -> list[dict]:
    return query_engine.recent_traces(limit=limit)


@app.get("/trace/{trace_id}")
def trace(trace_id: str) -> list[dict]:
    rows = query_engine.recent_traces(limit=5000)
    return [r for r in rows if r["trace_id"] == trace_id]


@app.get("/analytics")
def analytics(limit: int = 1000) -> dict:
    return _analytics_payload(limit)


@app.get("/analytics/export", response_class=PlainTextResponse)
def analytics_export(
    limit: int = 1000,
    format: str = Query(default="csv", pattern="^(csv|json)$"),
) -> str:
    rows = query_engine.recent_traces(limit=limit)
    df = pd.DataFrame(rows)

    if format == "json":
        return df.to_json(orient="records") if not df.empty else "[]"

    if df.empty:
        return ""

    sio = StringIO()
    df.to_csv(sio, index=False)
    return sio.getvalue()


@app.post("/analytics/rollups/run")
def run_rollup_now() -> dict:
    return rollup_worker.run_once()


@app.get("/analytics/rollups")
def get_rollups(limit: int = 100) -> list[dict]:
    return rollup_worker.recent_rollups(limit=limit)
