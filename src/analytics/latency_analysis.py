"""Latency analytics utilities."""

import pandas as pd


def latency_percentiles(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
    return {
        "p50": float(df["latency_ms"].quantile(0.50)),
        "p95": float(df["latency_ms"].quantile(0.95)),
        "p99": float(df["latency_ms"].quantile(0.99)),
    }
