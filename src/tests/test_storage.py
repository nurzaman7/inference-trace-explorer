from src.storage.sqlite_store import SQLiteStore


def test_sqlite_insert_and_fetch(tmp_path):
    db = SQLiteStore(str(tmp_path / "t.db"))
    db.insert_trace({
        "trace_id": "t1",
        "span_id": "s1",
        "timestamp": "2026-01-01T00:00:00Z",
        "input": "hello",
        "output": "world",
        "latency_ms": 1.2,
        "tokens_in": 1,
        "tokens_out": 1,
        "memory_mb": 100.0,
        "status": "success",
        "error": None,
    })
    rows = db.fetch_traces(limit=5)
    assert len(rows) == 1
