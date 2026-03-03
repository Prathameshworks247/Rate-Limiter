# Rate-Limiter

## Prometheus + Grafana

### What was added
- Prometheus metrics endpoint: `GET /metrics`
- Request metrics in app:
  - `http_requests_total`
  - `http_request_duration_seconds`
  - `rate_limited_requests_total`
- Docker Compose stack:
  - `app` on port `8000`
  - `prometheus` on port `9090`
  - `grafana` on port `3000`
- Auto-provisioned Grafana datasource pointing to Prometheus

### Run
```bash
docker compose up -d --build
```

### Verify
- API: `http://localhost:8000/unlimited`
- Metrics: `http://localhost:8000/metrics`
- Prometheus UI: `http://localhost:9090`
- Grafana UI: `http://localhost:3000` (login: `admin` / `admin`)

### Useful PromQL
- Request rate:
```promql
sum(rate(http_requests_total[1m])) by (path, status)
```
- P95 latency:
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, path))
```
- Rate-limited requests:
```promql
sum(rate(rate_limited_requests_total[1m])) by (path)
```
