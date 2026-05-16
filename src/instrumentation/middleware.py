"""FastAPI middleware for request-level tracing."""

from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.tracing.tracer import tracer


class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tracer.start_trace()
        started = perf_counter()
        response = await call_next(request)
        response.headers["x-latency-ms"] = f"{(perf_counter() - started) * 1000:.2f}"
        return response
