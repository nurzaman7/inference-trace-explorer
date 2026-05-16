import pandas as pd
from src.analytics.latency_analysis import latency_percentiles


def test_latency_percentiles_keys():
    df = pd.DataFrame([{"latency_ms": 10}, {"latency_ms": 20}, {"latency_ms": 30}])
    result = latency_percentiles(df)
    assert "p50" in result and "p95" in result and "p99" in result
