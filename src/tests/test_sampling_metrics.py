from fastapi.testclient import TestClient

from src import api as api_module


def test_sampling_metrics_endpoint_exists():
    client = TestClient(api_module.app)
    res = client.get("/metrics/sampling")
    assert res.status_code == 200
    data = res.json()
    assert "sample_rate" in data
    assert "seen_total" in data
    assert "kept_total" in data
    assert "dropped_total" in data
