from src.tracing.tracer import tracer


def test_start_trace_generates_ids():
    trace_id, span_id = tracer.start_trace()
    assert trace_id
    assert span_id
