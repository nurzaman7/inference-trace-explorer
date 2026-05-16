"""Pydantic request models for public APIs."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class InferRequest(BaseModel):
    prompt: str


class Message(BaseModel):
    role: str
    content: str


class OpenAICompatibleRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = 0.2
    max_tokens: int = 256
    base_url: str = "https://api.openai.com/v1"
    api_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnthropicRequest(BaseModel):
    model: str
    messages: list[Message]
    system: str | None = None
    temperature: float = 0.2
    max_tokens: int = 256
    base_url: str = "https://api.anthropic.com"
    api_key: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExternalTraceRecord(BaseModel):
    trace_id: str
    span_id: str
    timestamp: str
    input: str
    output: str
    latency_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    memory_mb: float = 0.0
    status: str = "success"
    error: str | None = None
    provider: str | None = None
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BulkIngestRequest(BaseModel):
    count: int = Field(default=1000, ge=1, le=200000)
    seed: int = 42
