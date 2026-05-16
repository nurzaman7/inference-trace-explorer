"""OpenAI-compatible chat completion client.

Works with OpenAI and any vendor exposing `/v1/chat/completions`.
"""

from __future__ import annotations

from typing import Any
import httpx


class OpenAICompatibleClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 256,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if extra:
            payload.update(extra)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()


def extract_text(response: dict[str, Any]) -> str:
    """Best-effort extraction for OpenAI-compatible responses."""
    choices = response.get("choices", [])
    if not choices:
        return ""
    first = choices[0]
    message = first.get("message", {})
    return str(message.get("content", ""))
