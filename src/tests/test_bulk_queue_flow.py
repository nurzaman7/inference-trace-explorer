from fastapi.testclient import TestClient

from src import api as api_module


def test_bulk_ingest_updates_queue_metrics():
    client = TestClient(api_module.app)

    before = client.get("/metrics/queue")
    assert before.status_code == 200

    res = client.post("/ingest/bulk", json={"count": 50, "seed": 123})
    assert res.status_code == 200

    after = client.get("/metrics/queue")
    assert after.status_code == 200
    metrics = after.json()
    assert metrics["enqueued_total"] >= 50
