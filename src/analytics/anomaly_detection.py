"""Simple z-score anomaly detector for latency spikes."""

import pandas as pd


def latency_anomalies(df: pd.DataFrame, threshold: float = 3.0) -> int:
    if df.empty or len(df) < 3:
        return 0
    col = df["latency_ms"]
    z = (col - col.mean()) / (col.std() or 1.0)
    return int((z.abs() > threshold).sum())
