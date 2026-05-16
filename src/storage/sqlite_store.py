"""SQLite trace storage backend."""

import sqlite3
from pathlib import Path
from src.storage.schema import TRACE_TABLE_SQL


class SQLiteStore:
    def __init__(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with sqlite3.connect(self.path) as conn:
            conn.execute(TRACE_TABLE_SQL)

    def insert_trace(self, row: dict) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO traces VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row.get("trace_id"),
                    row.get("span_id"),
                    row.get("timestamp"),
                    row.get("input"),
                    row.get("output"),
                    row.get("latency_ms"),
                    row.get("tokens_in"),
                    row.get("tokens_out"),
                    row.get("memory_mb"),
                    row.get("status"),
                    row.get("error"),
                ),
            )

    def fetch_traces(self, limit: int = 100) -> list[dict]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM traces ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
