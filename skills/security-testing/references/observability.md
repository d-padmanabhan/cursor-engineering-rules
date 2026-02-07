# Observability

## Three Pillars

### Logs

- Event records with context
- Structured format (JSON)
- Centralized collection

### Metrics

- Numerical measurements over time
- Counters, gauges, histograms
- Alerting thresholds

### Traces

- Request flow across services
- Distributed tracing
- Performance analysis

## Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

logger = logging.getLogger(__name__)
logger.info("User action", extra={
    "user_id": user.id,
    "action": "login",
    "ip": request.remote_addr
})
```

## Log Levels

| Level | Use When |
|-------|----------|
| DEBUG | Detailed diagnostic information |
| INFO | Normal operations, events |
| WARNING | Unexpected but handled situations |
| ERROR | Errors that need attention |
| CRITICAL | System failures |

## Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Counter - monotonically increasing
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# Histogram - distribution of values
request_latency = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

# Gauge - can go up or down
active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

# Usage
@app.before_request
def before():
    g.start_time = time.time()

@app.after_request
def after(response):
    latency = time.time() - g.start_time
    request_latency.labels(
        method=request.method,
        endpoint=request.path
    ).observe(latency)
    request_count.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    return response
```

## Tracing

```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span(
        "process_order",
        kind=SpanKind.INTERNAL
    ) as span:
        span.set_attribute("order_id", order_id)
        
        # Nested span
        with tracer.start_as_current_span("validate_order"):
            validate(order_id)
        
        with tracer.start_as_current_span("charge_payment"):
            charge(order_id)
```

## Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.endpoint }}"
      
      - alert: SlowResponses
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 10m
        labels:
          severity: warning
```

## Health Checks

```python
@app.route("/health")
def health():
    return {"status": "healthy"}

@app.route("/ready")
def ready():
    checks = {
        "database": check_database(),
        "cache": check_cache(),
        "external_api": check_external_api()
    }
    
    if all(checks.values()):
        return {"status": "ready", "checks": checks}
    else:
        return {"status": "not_ready", "checks": checks}, 503
```

## Dashboard Essentials

### RED Method (Request-focused)

- **R**ate: Requests per second
- **E**rrors: Error rate
- **D**uration: Latency distribution

### USE Method (Resource-focused)

- **U**tilization: How busy
- **S**aturation: Queue depth
- **E**rrors: Error count
