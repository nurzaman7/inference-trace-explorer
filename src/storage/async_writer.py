"""Background persistence worker for high-throughput trace ingestion."""

from __future__ import annotations

from queue import Empty, Full, Queue
from threading import Event, Lock, Thread
from typing import Any

from src.storage.jsonl_store import JSONLStore
from src.storage.sqlite_store import SQLiteStore
from src.utils.logger import get_logger


class AsyncTraceWriter:
    def __init__(
        self,
        sqlite_store: SQLiteStore,
        jsonl_store: JSONLStore,
        *,
        max_queue_size: int = 10_000,
        batch_size: int = 100,
    ) -> None:
        self.sqlite_store = sqlite_store
        self.jsonl_store = jsonl_store
        self.batch_size = batch_size
        self._q: Queue[dict[str, Any]] = Queue(maxsize=max_queue_size)
        self._stop = Event()
        self._thread: Thread | None = None
        self._log = get_logger("async_trace_writer")

        self._lock = Lock()
        self._enqueued_total = 0
        self._dropped_total = 0
        self._written_total = 0
        self._flush_batches_total = 0
        self._errors_total = 0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, name="trace-writer", daemon=True)
        self._thread.start()

    def enqueue(self, record: dict[str, Any]) -> bool:
        try:
            self._q.put_nowait(record)
            with self._lock:
                self._enqueued_total += 1
            return True
        except Full:
            self._log.warning("trace queue full; dropping record")
            with self._lock:
                self._dropped_total += 1
            return False

    def stop(self, timeout: float = 3.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def flush_sync(self, record: dict[str, Any]) -> None:
        """Fallback synchronous write path when queue is full."""
        self.jsonl_store.append(record)
        self.sqlite_store.insert_trace(record)
        with self._lock:
            self._written_total += 1

    def metrics(self) -> dict[str, int]:
        with self._lock:
            return {
                "queue_depth": self._q.qsize(),
                "enqueued_total": self._enqueued_total,
                "dropped_total": self._dropped_total,
                "written_total": self._written_total,
                "flush_batches_total": self._flush_batches_total,
                "errors_total": self._errors_total,
            }

    def _run(self) -> None:
        pending: list[dict[str, Any]] = []
        while not self._stop.is_set() or not self._q.empty():
            try:
                pending.append(self._q.get(timeout=0.25))
            except Empty:
                pass

            if not pending:
                continue

            if len(pending) >= self.batch_size or self._stop.is_set() or self._q.empty():
                self._flush_batch(pending)
                pending.clear()

    def _flush_batch(self, batch: list[dict[str, Any]]) -> None:
        try:
            for record in batch:
                self.jsonl_store.append(record)
                self.sqlite_store.insert_trace(record)
            with self._lock:
                self._written_total += len(batch)
                self._flush_batches_total += 1
        except Exception:
            self._log.exception("failed to flush trace batch")
            with self._lock:
                self._errors_total += 1
