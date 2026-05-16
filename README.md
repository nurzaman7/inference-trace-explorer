# Inference Trace Explorer

Inference Trace Explorer is a production-inspired observability tool for AI inference systems.

It helps teams:
- trace inference calls
- capture telemetry metadata
- store/search traces
- simulate activation extraction
- analyze latency/errors/tokens
- integrate with OpenAI, Claude, and OpenAI-compatible providers

## What You Get

- FastAPI backend for tracing and ingestion
- SQLite + JSONL storage
- Streamlit dashboard with live queue health cards
- Integration endpoints for major LLM APIs
- Analytics endpoints (p50/p95/p99, error rate, anomalies)

## Project Structure

- `src/api.py`: FastAPI service
- `src/integrations/`: OpenAI-compatible + Anthropic clients
- `src/models/`: local inference simulation engine
- `src/tracing/`: trace/span context and decorators
- `src/storage/`: SQLite + JSONL stores
- `src/analytics/`: latency/token/error/anomaly analysis
- `src/dashboard/`: Streamlit UI
- `docs/API_INTEGRATIONS.md`: integration cookbook

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.api:app --reload
```

Open API docs:
- http://localhost:8000/docs

Run dashboard:

```bash
streamlit run src/dashboard/streamlit_app.py
```

## API Endpoints

### Core
- `GET /health`
- `POST /infer`
- `GET /traces`
- `GET /trace/{trace_id}`
- `GET /analytics`
- `GET /metrics/queue`
- `GET /metrics/sampling`
- `GET /otel/spans`

### Integration & Ingestion
- `POST /integrations/openai/chat`
- `POST /integrations/anthropic/messages`
- `POST /ingest/trace`
- `POST /ingest/bulk`

## Integrating with OpenAI / Claude / Agentic Systems

1. For direct OpenAI calls, use `POST /integrations/openai/chat`
2. For Claude calls, use `POST /integrations/anthropic/messages`
3. For any external agent framework (LangChain, custom workers), push normalized traces to `POST /ingest/trace`

Detailed examples:
- [`docs/API_INTEGRATIONS.md`](docs/API_INTEGRATIONS.md)

## Environment Variables

Defined in `.env.example`:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `SQLITE_PATH`
- `JSONL_TRACE_PATH`

## Typical Workflow

1. Send model requests through integration endpoints.
2. Trace records auto-persist to JSONL + SQLite.
3. Query traces with `/traces` or `/trace/{trace_id}`.
4. Monitor aggregates via `/analytics` and Streamlit dashboard.
5. Monitor write-path health via `/metrics/queue` (depth, drops, flushes, errors).

## Notes

- Provider token usage is parsed from provider responses when available (OpenAI/Anthropic).
- Provider response payloads are retained in JSONL traces for debugging.
- SQLite schema is intentionally simple for fast local iteration.


## Dashboard Queue Health Cards

The Streamlit dashboard now shows live writer metrics from `GET /metrics/queue`:
- Queue depth
- Enqueued total
- Written total
- Dropped total
- Flush batch count
- Writer errors

You can override API target using `API_BASE_URL` in `.env`.


## Load Generation (100k+ traces)

Bulk-generate and enqueue synthetic traces:

```bash
curl -X POST http://localhost:8000/ingest/bulk \
  -H "Content-Type: application/json" \
  -d "{\"count\":100000,\"seed\":42}"
```

Run benchmark helper:

```bash
python examples/load_benchmark.py --count 100000
```


## Analytics Export and Rollups

Export recent traces for BI/reporting:

```bash
curl "http://localhost:8000/analytics/export?format=csv&limit=5000"
```

Trigger immediate summary rollup:

```bash
curl -X POST http://localhost:8000/analytics/rollups/run
```

Read recent rollup snapshots:

```bash
curl "http://localhost:8000/analytics/rollups?limit=20"
```


## Sampling Control

Use `TRACE_SAMPLE_RATE` in `.env` to control ingestion volume (0.0-1.0).
Monitor behavior with:

```bash
curl http://localhost:8000/metrics/sampling
```


## Project Operations

- Contributor guide: `CONTRIBUTING.md`
- Production-style runbook: `docs/RUNBOOK.md`

## OpenTelemetry Adapter

Export OTEL-like spans for downstream collector compatibility:

```bash
curl "http://localhost:8000/otel/spans?limit=200"
```
