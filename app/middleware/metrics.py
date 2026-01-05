import time
from fastapi import Request
from prometheus_client import Counter, Histogram


REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["status_group"])

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["status_group"]
)


async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    status = response.status_code
    if 200 <= status < 300:
        group = "2xx"
    elif 400 <= status < 500:
        group = "4xx"
    elif 500 <= status < 600:
        group = "5xx"
    else:
        group = str(status)

    REQUEST_COUNT.labels(status_group=group).inc()
    REQUEST_LATENCY.labels(status_group=group).observe(duration)

    return response
