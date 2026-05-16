"""Inference engine that emits telemetry and synthetic activations."""

from datetime import datetime, UTC
from time import perf_counter
from src.models.llm_wrapper import LLMWrapper
from src.tracing.tracer import tracer
from src.instrumentation.monitor import memory_mb
from src.activations.extractor import simulate_layers


class InferenceEngine:
    def __init__(self) -> None:
        self.wrapper = LLMWrapper()

    def infer(self, prompt: str) -> dict:
        trace_id, span_id = tracer.start_trace()
        started = perf_counter()
        status = "success"
        error = None
        try:
            output = self.wrapper.run(prompt)
        except Exception as exc:  # pragma: no cover
            output = ""
            status = "error"
            error = str(exc)

        latency = (perf_counter() - started) * 1000
        return {
            "trace_id": trace_id,
            "span_id": span_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "input": prompt,
            "output": output,
            "latency_ms": round(latency, 3),
            "tokens_in": len(prompt.split()),
            "tokens_out": len(output.split()),
            "memory_mb": round(memory_mb(), 3),
            "status": status,
            "error": error,
            "activations": simulate_layers(),
        }
