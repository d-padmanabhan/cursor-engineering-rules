# Python Logging

Use the observability skill
(`${HANDBOOK_ROOT}/skills/observability/SKILL.md`) for signal design, schemas,
metrics, tracing, SLOs, alerts, telemetry pipelines, and security policy. This
reference owns Python runtime integration only.

## Configuration Ownership

- Applications configure handlers, formatters, destinations, and levels once at
  the process entry point.
- Libraries use `logging.getLogger(__name__)` and do not add handlers or change
  the root level.
- Prefer the standard library unless an existing structured-logging dependency
  provides capabilities the service needs.
- For containers, write structured events to `stdout` or `stderr`; let the
  platform collect and rotate them.
- Read the level from validated configuration. Do not enable debug logging in
  production by default.

## Allowlisted JSON Formatter

Do not copy every `LogRecord` attribute or arbitrary `extra` value into output.
Define a bounded allowlist:

```python
import json
import logging
from datetime import UTC, datetime
from typing import Any

ALLOWED_CONTEXT_FIELDS = (
    "event_name",
    "trace_id",
    "span_id",
    "request_id",
    "operation",
    "outcome",
)


class JsonFormatter(logging.Formatter):
    """Encode an allowlisted log event as one JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        """Return a bounded JSON representation of the record."""
        event: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "severity_text": record.levelname,
            "logger": record.name,
            "body": record.getMessage(),
        }

        for field in ALLOWED_CONTEXT_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                event[field] = value

        if record.exc_info is not None:
            exception_type = record.exc_info[0]
            event["error.type"] = exception_type.__name__

        return json.dumps(event, ensure_ascii=False, separators=(",", ":"))


def configure_logging(level: int = logging.INFO) -> None:
    """Configure process-wide structured logging at the application boundary."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
```

This example is a starting point, not a complete production schema. It
intentionally omits exception messages and stacks. Bound the body before
adopting it in a high-volume or adversarial service.

## Context

Use `extra` only with allowlisted fields:

```python
logger = logging.getLogger(__name__)

logger.info(
    "Request completed",
    extra={
        "event_name": "http.request.completed",
        "trace_id": trace_id,
        "span_id": span_id,
        "request_id": request_id,
        "operation": "POST /orders",
        "outcome": "accepted",
    },
)
```

Inject trace and request context through framework middleware, an
OpenTelemetry-compatible logging bridge, `LoggerAdapter`, a filter, or
`contextvars`. Do not pass context manually through every function when the
runtime already has request-local context.

Validate externally supplied identifiers for format and length. Trace,
request, and correlation identifiers are diagnostic context, not authorization
evidence.

## Exceptions

- Log an exception once at the boundary that decides the operation outcome.
- Include a stack only in a policy-approved sink with redaction and a strict
  size limit.
- Do not log and rethrow the same exception at every layer.
- Bound and scrub exception messages and stacks because dependencies may embed
  payload fragments or secrets.
- Use stable `error.type` and domain error codes for queries; do not parse the
  human-readable message.

```python
try:
    process_request()
except ProviderTimeout:
    logger.error(
        "Provider request failed",
        exc_info=True,
        extra={
            "event_name": "provider.request.failed",
            "request_id": request_id,
            "operation": "provider.fetch",
            "outcome": "timeout",
        },
    )
    raise
```

## Sensitive Data

Never log authorization headers, cookies, tokens, private keys, secret values,
raw request or response bodies, or unrestricted object representations.
Minimize email addresses, IP addresses, user identifiers, and other personal
data. Apply schema-based redaction before serialization and test it with hostile
fixtures.

Avoid f-strings for structured attributes:

```python
# Avoid: variable data is embedded in prose and may expose the object.
logger.info(f"Processed request {request}")

# Prefer: stable message plus allowlisted bounded attributes.
logger.info(
    "Request processed",
    extra={
        "event_name": "request.processed",
        "request_id": request_id,
        "outcome": "success",
    },
)
```

## Verification

- Parse every emitted line as JSON in formatter tests.
- Test values containing newlines, control characters, and non-ASCII text.
- Verify secret and sensitive-field fixtures never appear.
- Test context isolation across concurrent tasks and requests.
- Confirm trace and span identifiers match the active context.
- Measure logging overhead and event volume under representative load.
- Verify output in the actual collector and backend.
