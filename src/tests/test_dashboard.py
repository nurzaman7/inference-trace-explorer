import pandas as pd

from src.dashboard.filters import by_status
from src.dashboard.metrics import fetch_queue_metrics


def test_dashboard_filter_status():
    df = pd.DataFrame([{"status": "success"}, {"status": "error"}])
    assert len(by_status(df, "success")) == 1


def test_fetch_queue_metrics_unreachable_returns_zeros():
    data = fetch_queue_metrics("http://127.0.0.1:9", timeout_s=0.05)
    assert data["queue_depth"] == 0
    assert data["errors_total"] == 0
