from time import perf_counter
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from services.rate_limiter import RateLimitFactory
from algortihms.limiting_algorithms import RateLimitExceeded

app = FastAPI()
ip_addresses = {}

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
RATE_LIMITED_COUNT = Counter(
    "rate_limited_requests_total",
    "Total requests rejected by rate limiter",
    ["path"],
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = perf_counter()
    path = request.url.path
    method = request.method
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        REQUEST_COUNT.labels(method=method, path=path, status=str(status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(perf_counter() - start_time)


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/limited")
def limited(request: Request):
    client = request.client.host
    try:
        if client not in ip_addresses:
            ip_addresses[client] = RateLimitFactory.get_instance("FixedCounterWindow")
        if ip_addresses[client].allow_request(client):
            return "This is a limited use API"
    except RateLimitExceeded as e:
        RATE_LIMITED_COUNT.labels(path=request.url.path).inc()
        raise e

@app.get("/unlimited")
def unlimited(request: Request):
    return "Free to use API limitless"
