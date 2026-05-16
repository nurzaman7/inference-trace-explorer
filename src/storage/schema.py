"""SQLite schema DDL."""

TRACE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT,
    span_id TEXT,
    timestamp TEXT,
    input TEXT,
    output TEXT,
    latency_ms REAL,
    tokens_in INTEGER,
    tokens_out INTEGER,
    memory_mb REAL,
    status TEXT,
    error TEXT
);
"""
