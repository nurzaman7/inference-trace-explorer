"""Integration service that invokes providers and emits trace-like records."""

from __future__ import annotations

from datetime import datetime, UTC
from time import perf_counter
from typing import Any

from src.instrumentation.monitor import memory_mb
from src.tracing.tracer import tracer
from src.integrations.openai_compatible import OpenAICompatibleClient, extract_text as extract_openai_text
from src.integrations.anthropic_client import AnthropicClient, extract_text as extract_anthropic_text


def _count_tokens_rough(text: str) -> int:
    return len(text.split())


def _openai_token_usage(response: dict[str, Any], prompt_text: str, output_text: str) -> tuple[int, int]:
    usage = response.get("usage", {})
    in_tok = usage.get("prompt_tokens")
    out_tok = usage.get("completion_tokens")
    if isinstance(in_tok, int) and isinstance(out_tok, int):
        return in_tok, out_tok
    return _count_tokens_rough(prompt_text), _count_tokens_rough(output_text)


def _anthropic_token_usage(response: dict[str, Any], prompt_text: str, output_text: str) -> tuple[int, int]:
    usage = response.get("usage", {})
    in_tok = usage.get("input_tokens")
    out_tok = usage.get("output_tokens")
    if isinstance(in_tok, int) and isinstance(out_tok, int):
        return in_tok, out_tok
    return _count_tokens_rough(prompt_text), _count_tokens_rough(output_text)


class IntegrationService:
    def call_openai_compatible(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 256,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace_id, span_id = tracer.start_trace()
        started = perf_counter()
        status = "success"
        error = None

        try:
            raw = OpenAICompatibleClient(api_key=api_key, base_url=base_url).chat_completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            output = extract_openai_text(raw)
        except Exception as exc:  # pragma: no cover
            raw = {"error": str(exc)}
            output = ""
            status = "error"
            error = str(exc)

        latency_ms = (perf_counter() - started) * 1000
        prompt_text = "\n".join(m.get("content", "") for m in messages)
        tokens_in, tokens_out = _openai_token_usage(raw, prompt_text, output)

        return {
            "trace_id": trace_id,
            "span_id": span_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "input": prompt_text,
            "output": output,
            "latency_ms": round(latency_ms, 3),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "memory_mb": round(memory_mb(), 3),
            "status": status,
            "error": error,
            "provider": "openai-compatible",
            "model": model,
            "metadata": metadata or {},
            "provider_response": raw,
        }

    def call_anthropic(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 256,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace_id, span_id = tracer.start_trace()
        started = perf_counter()
        status = "success"
        error = None

        try:
            raw = AnthropicClient(api_key=api_key, base_url=base_url).create_message(
                model=model,
                messages=messages,
                system=system,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            output = extract_anthropic_text(raw)
        except Exception as exc:  # pragma: no cover
            raw = {"error": str(exc)}
            output = ""
            status = "error"
            error = str(exc)

        latency_ms = (perf_counter() - started) * 1000
        prompt_text = "\n".join(m.get("content", "") for m in messages)
        tokens_in, tokens_out = _anthropic_token_usage(raw, prompt_text, output)

        return {
            "trace_id": trace_id,
            "span_id": span_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "input": prompt_text,
            "output": output,
            "latency_ms": round(latency_ms, 3),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "memory_mb": round(memory_mb(), 3),
            "status": status,
            "error": error,
            "provider": "anthropic",
            "model": model,
            "metadata": metadata or {},
            "provider_response": raw,
        }
