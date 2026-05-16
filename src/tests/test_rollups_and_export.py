from fastapi.testclient import TestClient

from src import api as api_module


def test_analytics_export_csv_endpoint():
    client = TestClient(api_module.app)
    res = client.get("/analytics/export", params={"limit": 10, "format": "csv"})
    assert res.status_code == 200
    assert isinstance(res.text, str)


def test_rollup_run_and_fetch():
    client = TestClient(api_module.app)
    run = client.post("/analytics/rollups/run")
    assert run.status_code == 200
    body = run.json()
    assert "timestamp" in body

    fetch = client.get("/analytics/rollups", params={"limit": 5})
    assert fetch.status_code == 200
    assert isinstance(fetch.json(), list)
