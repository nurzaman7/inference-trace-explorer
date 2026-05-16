"""Reusable tracing decorators."""

from functools import wraps
from time import perf_counter
from src.tracing.tracer import tracer


def capture_latency(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        _ = (perf_counter() - start) * 1000
        return result

    return wrapper


def trace_function(name: str | None = None):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            span = tracer.start_span(name or func.__name__)
            start = perf_counter()
            try:
                result = func(*args, **kwargs)
                tracer.end_span(span, (perf_counter() - start) * 1000)
                return result
            except Exception as exc:  # pragma: no cover
                tracer.end_span(span, (perf_counter() - start) * 1000, status="error", error=str(exc))
                raise

        return wrapper

    return deco


def trace_model(func):
    return trace_function("model_inference")(func)
