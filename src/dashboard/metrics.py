"""Dashboard metrics data-access helpers."""

from __future__ import annotations

import httpx


def fetch_queue_metrics(api_base_url: str, timeout_s: float = 3.0) -> dict:
    """Fetch queue writer metrics from API.

    Returns empty counters if API is unreachable.
    """
    url = f"{api_base_url.rstrip('/')}/metrics/queue"
    try:
        with httpx.Client(timeout=timeout_s) as client:
            res = client.get(url)
            res.raise_for_status()
            data = res.json()
            return {
                "queue_depth": int(data.get("queue_depth", 0)),
                "enqueued_total": int(data.get("enqueued_total", 0)),
                "dropped_total": int(data.get("dropped_total", 0)),
                "written_total": int(data.get("written_total", 0)),
                "flush_batches_total": int(data.get("flush_batches_total", 0)),
                "errors_total": int(data.get("errors_total", 0)),
            }
    except Exception:
        return {
            "queue_depth": 0,
            "enqueued_total": 0,
            "dropped_total": 0,
            "written_total": 0,
            "flush_batches_total": 0,
            "errors_total": 0,
        }
