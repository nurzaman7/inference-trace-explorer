# API Integrations: OpenAI, Claude, and OpenAI-Compatible LLMs

This project exposes provider-ready endpoints so teams can trace real model calls while keeping a unified telemetry format.

## 1) Start Service

```bash
uvicorn src.api:app --reload
```

## 2) Core Local Inference (simulated)

```bash
curl -X POST http://localhost:8000/infer \
  -H "Content-Type: application/json" \
  -d '{"prompt":"summarize device telemetry anomalies"}'
```

## 3) OpenAI Integration

Endpoint:
- `POST /integrations/openai/chat`

Request:

```bash
curl -X POST http://localhost:8000/integrations/openai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model":"gpt-4o-mini",
    "messages":[
      {"role":"system","content":"You are an observability assistant."},
      {"role":"user","content":"Find likely causes of inference latency spikes."}
    ],
    "temperature":0.2,
    "max_tokens":180,
    "metadata":{"team":"platform","service":"trace-explorer"}
  }'
```

Auth options:
- set `OPENAI_API_KEY` in `.env`
- or pass `api_key` in the JSON body

## 4) Claude (Anthropic) Integration

Endpoint:
- `POST /integrations/anthropic/messages`

Request:

```bash
curl -X POST http://localhost:8000/integrations/anthropic/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model":"claude-3-5-sonnet-latest",
    "system":"You are a production incident analyst.",
    "messages":[
      {"role":"user","content":"Analyze throughput regression from traces."}
    ],
    "temperature":0.2,
    "max_tokens":180,
    "metadata":{"incident_id":"INC-421"}
  }'
```

Auth options:
- set `ANTHROPIC_API_KEY` in `.env`
- or pass `api_key` in the JSON body

## 5) Any OpenAI-Compatible Vendor

You can target local/hosted providers (vLLM, compatible gateways, etc.) by overriding `base_url`:

```json
{
  "model": "my-model",
  "base_url": "http://localhost:8080/v1",
  "messages": [{"role": "user", "content": "hello"}]
}
```

## 6) Bring Your Own Agent Traces

Endpoint:
- `POST /ingest/trace`

Use this to ingest traces from LangChain, custom agents, or worker pipelines.

```bash
curl -X POST http://localhost:8000/ingest/trace \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id":"abc123",
    "span_id":"root1",
    "timestamp":"2026-05-16T12:00:00Z",
    "input":"agent tool call payload",
    "output":"tool result",
    "latency_ms":43.2,
    "tokens_in":120,
    "tokens_out":38,
    "memory_mb":512,
    "status":"success",
    "provider":"custom-agent",
    "model":"router-v2",
    "metadata":{"workflow":"triage"}
  }'
```

## 7) Analytics and Search APIs

- `GET /traces?limit=200`
- `GET /trace/{trace_id}`
- `GET /analytics?limit=5000`

These let you power external UIs or agent debugging pipelines.


## 8) Queue Health Metrics

- `GET /metrics/queue`

Use this endpoint to monitor ingestion backpressure and write health:
- `queue_depth`
- `enqueued_total`
- `dropped_total`
- `written_total`
- `flush_batches_total`
- `errors_total`


## 9) Large-Scale Synthetic Trace Ingestion

Endpoint:
- `POST /ingest/bulk`

Example:

```bash
curl -X POST http://localhost:8000/ingest/bulk \
  -H "Content-Type: application/json" \
  -d "{\"count\":100000,\"seed\":42}"
```

This simulates high-scale telemetry pipelines and lets you validate queue backpressure behavior via `GET /metrics/queue`.


## 10) Exports and Rollups

- `GET /analytics/export?format=csv|json&limit=...`
- `POST /analytics/rollups/run`
- `GET /analytics/rollups?limit=...`

Use these for external reporting, scheduled jobs, or offline analysis pipelines.


## 11) OpenTelemetry Adapter

- `GET /otel/spans?limit=...&service_name=...`

Returns OTEL-like span payloads derived from stored traces for collector or pipeline compatibility.
