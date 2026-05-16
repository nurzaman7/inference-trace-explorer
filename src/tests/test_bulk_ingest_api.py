from fastapi.testclient import TestClient

from src import api as api_module


def test_bulk_ingest_endpoint_small_batch():
    client = TestClient(api_module.app)
    res = client.post("/ingest/bulk", json={"count": 25, "seed": 7})
    assert res.status_code == 200
    data = res.json()
    assert data["requested"] == 25
    assert data["accepted"] >= 0
    assert "enqueue_rate_per_sec" in data
