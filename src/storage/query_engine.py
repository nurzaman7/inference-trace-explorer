"""Simple query abstraction over storage backends."""

from src.storage.sqlite_store import SQLiteStore


class QueryEngine:
    def __init__(self, sqlite_store: SQLiteStore) -> None:
        self.sqlite_store = sqlite_store

    def recent_traces(self, limit: int = 100) -> list[dict]:
        return self.sqlite_store.fetch_traces(limit=limit)
