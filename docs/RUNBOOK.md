# Runbook

## Start Services

```bash
docker compose up --build
```

API: `http://localhost:8000/docs`
Dashboard: `http://localhost:8501`

## Health Checks

- API health: `GET /health`
- Queue metrics: `GET /metrics/queue`
- Sampling metrics: `GET /metrics/sampling`

## Common Operations

### Generate load

```bash
curl -X POST http://localhost:8000/ingest/bulk \
  -H "Content-Type: application/json" \
  -d '{"count":100000,"seed":42}'
```

### Force rollup snapshot

```bash
curl -X POST http://localhost:8000/analytics/rollups/run
```

### Export traces for external analysis

```bash
curl "http://localhost:8000/analytics/export?format=csv&limit=5000"
```

### Export OTEL-like spans

```bash
curl "http://localhost:8000/otel/spans?limit=200"
```

## Incident Triage

1. Check `/metrics/queue` for queue growth and drops.
2. Check `/metrics/sampling` to confirm effective sampling.
3. Compare `/analytics` p95/p99 vs historical rollups.
4. Export suspect window via `/analytics/export` for offline analysis.

## Failure Modes

- High queue depth + growing drops:
  - increase sample rate aggressiveness (lower `TRACE_SAMPLE_RATE`)
  - increase writer throughput (batch size / storage tuning)
- High p99 spikes:
  - inspect provider-specific traces
  - check sampled-in/out ratio
