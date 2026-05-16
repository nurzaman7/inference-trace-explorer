"""Example client that sends one OpenAI-style request and prints trace ids."""

from __future__ import annotations

import os
import httpx


def main() -> None:
    base = os.getenv("TRACE_API_BASE", "http://localhost:8000")
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an observability assistant."},
            {"role": "user", "content": "Summarize p95 latency risk signals."},
        ],
        "temperature": 0.2,
        "max_tokens": 120,
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{base}/integrations/openai/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

    print("trace_id:", data.get("trace_id"))
    print("span_id:", data.get("span_id"))
    print("status:", data.get("status"))


if __name__ == "__main__":
    main()
