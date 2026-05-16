"""Background rollup worker for periodic analytics snapshots."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path
from threading import Event, Thread
from time import sleep

import pandas as pd

from src.analytics.anomaly_detection import latency_anomalies
from src.analytics.error_analysis import error_rate
from src.analytics.latency_analysis import latency_percentiles
from src.analytics.token_analysis import token_totals
from src.storage.query_engine import QueryEngine
from src.utils.logger import get_logger


class AnalyticsRollupWorker:
    def __init__(
        self,
        query_engine: QueryEngine,
        output_path: str,
        *,
        interval_seconds: int = 60,
        sample_limit: int = 50000,
    ) -> None:
        self.query_engine = query_engine
        self.output_path = Path(output_path)
        self.interval_seconds = interval_seconds
        self.sample_limit = sample_limit
        self._stop = Event()
        self._thread: Thread | None = None
        self._log = get_logger("analytics_rollup_worker")

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._thread = Thread(target=self._run, daemon=True, name="analytics-rollup")
        self._thread.start()

    def stop(self, timeout: float = 3.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def run_once(self) -> dict:
        rows = self.query_engine.recent_traces(limit=self.sample_limit)
        df = pd.DataFrame(rows)

        if df.empty:
            snapshot = {
                "timestamp": datetime.now(UTC).isoformat(),
                "count": 0,
                "latency": {"p50": 0.0, "p95": 0.0, "p99": 0.0},
                "error_rate": 0.0,
                "tokens": {"tokens_in": 0, "tokens_out": 0},
                "anomalies": 0,
            }
        else:
            snapshot = {
                "timestamp": datetime.now(UTC).isoformat(),
                "count": int(len(df)),
                "latency": latency_percentiles(df),
                "error_rate": error_rate(df),
                "tokens": token_totals(df),
                "anomalies": latency_anomalies(df),
            }

        with self.output_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(snapshot) + "\n")

        return snapshot

    def recent_rollups(self, limit: int = 100) -> list[dict]:
        if not self.output_path.exists():
            return []
        lines = self.output_path.read_text(encoding="utf-8").splitlines()
        out: list[dict] = []
        for ln in lines[-limit:]:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
        return out

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:
                self._log.exception("rollup tick failed")
            sleep(self.interval_seconds)
