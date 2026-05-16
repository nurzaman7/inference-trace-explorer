"""Synthetic high-volume trace generation utilities."""

from __future__ import annotations

from datetime import datetime, UTC, timedelta
from random import Random
from uuid import uuid4


def generate_trace_batch(count: int, seed: int = 42, start_time: datetime | None = None) -> list[dict]:
    rnd = Random(seed)
    now = start_time or datetime.now(UTC)
    batch: list[dict] = []

    for i in range(count):
        trace_id = uuid4().hex
        span_id = uuid4().hex[:16]

        # Realistic latency distribution with occasional spikes.
        base = max(1.0, rnd.gauss(85, 25))
        if rnd.random() < 0.02:
            base += rnd.uniform(300, 1200)

        status = "error" if rnd.random() < 0.03 else "success"
        err = "timeout" if status == "error" else None

        tokens_in = rnd.randint(10, 800)
        tokens_out = rnd.randint(20, 1200)
        mem = rnd.uniform(180, 900)

        ts = (now - timedelta(milliseconds=i * rnd.randint(1, 10))).isoformat()

        batch.append(
            {
                "trace_id": trace_id,
                "span_id": span_id,
                "timestamp": ts,
                "input": f"synthetic prompt {i}",
                "output": f"synthetic output {i}",
                "latency_ms": round(base, 3),
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "memory_mb": round(mem, 3),
                "status": status,
                "error": err,
                "provider": "loadgen",
                "model": "synthetic-v1",
                "metadata": {"batch_index": i},
            }
        )

    return batch
