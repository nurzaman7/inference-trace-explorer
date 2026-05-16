"""Simple benchmark script for bulk ingestion and queue behavior."""

from __future__ import annotations

import argparse
import time
import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    args = parser.parse_args()

    with httpx.Client(timeout=120.0) as client:
        start = time.perf_counter()
        res = client.post(f"{args.base.rstrip('/')}/ingest/bulk", json={"count": args.count, "seed": args.seed})
        res.raise_for_status()
        ingest_data = res.json()
        ingest_elapsed = time.perf_counter() - start

        print("bulk ingest:", ingest_data)
        print("request_elapsed_sec:", round(ingest_elapsed, 3))

        time.sleep(args.poll_seconds)
        q = client.get(f"{args.base.rstrip('/')}/metrics/queue")
        q.raise_for_status()
        print("queue_metrics:", q.json())

        analytics = client.get(f"{args.base.rstrip('/')}/analytics", params={"limit": min(args.count, 100000)})
        analytics.raise_for_status()
        print("analytics:", analytics.json())


if __name__ == "__main__":
    main()
