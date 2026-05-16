from fastapi.testclient import TestClient

from src import api as api_module


def test_queue_metrics_endpoint_shape():
    client = TestClient(api_module.app)
    res = client.get("/metrics/queue")
    assert res.status_code == 200
    data = res.json()
    for key in [
        "queue_depth",
        "enqueued_total",
        "dropped_total",
        "written_total",
        "flush_batches_total",
        "errors_total",
    ]:
        assert key in data
