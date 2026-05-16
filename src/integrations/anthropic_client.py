"""Anthropic Messages API client."""

from __future__ import annotations

from typing import Any
import httpx


class AnthropicClient:
    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def create_message(
        self,
        model: str,
        messages: list[dict[str, str]],
        system: str | None = None,
        max_tokens: int = 256,
        temperature: float = 0.2,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system:
            payload["system"] = system
        if extra:
            payload.update(extra)

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.base_url}/v1/messages", headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()


def extract_text(response: dict[str, Any]) -> str:
    blocks = response.get("content", [])
    texts: list[str] = []
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            texts.append(str(block.get("text", "")))
    return "\n".join(texts)
