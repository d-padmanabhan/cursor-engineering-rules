# AWS Lambda Best Practices

Apply these practices when they improve correctness, performance, security, or operability. Avoid adding abstractions that a small function does not need. SDK configuration, retries, errors, pagination, and waiters are defined in the canonical [AWS and Boto3 reference](aws-boto3.md).

## Structure and Handler

For handbook projects, use `main.py` as the Lambda entry module and configure the handler as `main.lambda_handler`. This is a repository convention, not an AWS platform requirement.

Place supporting functions before `lambda_handler` so the handler reads as the orchestration entry point. Use a descriptive context parameter when needed and prefix it when intentionally unused.

```python
def process_event(event: dict[str, object]) -> dict[str, object]:
    """Process a validated Lambda event."""
    return {"processed": True}


def lambda_handler(
    event: dict[str, object],
    context: object,
) -> dict[str, object]:
    """Handle a Lambda invocation."""
    return process_event(event)
```

```python
def lambda_handler(
    event: dict[str, object],
    _context: object,
) -> dict[str, object]:
    """Handle an invocation that does not use Lambda context."""
    return process_event(event)
```

Use event-source-specific types or validation models when the payload contract is known. A generic `dict[str, object]` is only a baseline.

## Client Initialization

Reuse frequently used AWS SDK clients across warm invocations by creating them at module scope. Lazy initialization is appropriate for clients needed only on uncommon paths when eager initialization would add unnecessary cold-start work.

Do not create a client on every invocation unless its configuration must vary per request. Passing clients into business functions improves testability. A client created inside a class is valid when the class instance itself is reused.

Use a cached factory only when clients vary by bounded, validated configuration. Do not introduce a singleton manager for one fixed client. See [AWS and Boto3](aws-boto3.md) for the canonical client configuration.

## Dry-Run Behavior

Add dry-run behavior only when every side effect can be completely and reliably suppressed.

- Prefer deployment configuration or a validated environment variable over an untrusted event field.
- If an event flag is necessary, accept it only from a trusted event source and validate that it is a boolean.
- Suppress every write, delete, notification, queue publish, and external mutation, not just the primary action.
- Do not log complete payloads, secrets, or sensitive values while previewing actions.

```python
import os


def dry_run_enabled() -> bool:
    """Return whether deployment-configured dry-run mode is enabled."""
    return os.getenv("DRY_RUN") == "1"
```

## Logging and Correlation

Use structured JSON logs suitable for CloudWatch Logs Insights. Configure Lambda's advanced logging controls through infrastructure as code, or use a structured logger when it provides required capabilities.

Include `context.aws_request_id` and a stable upstream identifier when available. Propagate an existing correlation ID across service boundaries rather than replacing it at every hop.

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(
    event: dict[str, object],
    context: object,
) -> dict[str, object]:
    """Handle an EventBridge event with correlation fields."""
    request_id = getattr(context, "aws_request_id", None)
    event_id = event.get("id")
    logger.info(
        "Processing event",
        extra={
            "aws_request_id": request_id,
            "event_id": event_id,
        },
    )
    return process_event(event)
```

Do not log complete events by default. Events can contain credentials, authorization headers, personal data, secrets, or large payloads. Redact sensitive fields and log only the identifiers needed to operate the function.

AWS Lambda supports native JSON formatting for Python standard-library logs. See [Using structured JSON logs with Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html).

## Powertools for AWS Lambda

Use Powertools when it replaces meaningful custom code or provides required capabilities such as:

- Structured logging and correlation
- Event parsing and validation
- Custom metrics
- Idempotency
- Batch processing or parameter retrieval

Do not add Powertools solely because code runs in Lambda. If native structured logging and existing utilities already meet the requirements, another dependency may not add value.

When using the Logger utility, event logging remains opt-in. Do not enable full-event logging without a reviewed data-classification and redaction decision.

```python
from aws_lambda_powertools import Logger

logger = Logger()


@logger.inject_lambda_context
def lambda_handler(
    event: dict[str, object],
    context: object,
) -> dict[str, object]:
    """Handle an invocation with Lambda context fields."""
    logger.info("Processing invocation")
    return process_event(event)
```

See the official [Powertools for AWS Lambda overview](https://docs.aws.amazon.com/lambda/latest/dg/powertools-for-lambda.html).

## Tracing

Treat tracing as a separate observability change with its own testing and operational review.

- Enable Lambda Active Tracing and configure sampling and IAM through infrastructure as code.
- Prefer the AWS-managed OpenTelemetry Lambda layer or another reviewed OpenTelemetry setup for new application instrumentation.
- Instrument relevant AWS SDK and outbound HTTP calls.
- Evaluate cold-start latency, package size, telemetry cost, sampling behavior, and sensitive-data exposure.
- Do not add new instrumentation based on the AWS X-Ray SDK. AWS placed the X-Ray SDKs and daemon into maintenance mode on February 25, 2026 and recommends migration to OpenTelemetry.
- Keep logs, metrics, and traces complementary; none replaces the others.

See AWS guidance for [migrating X-Ray instrumentation to OpenTelemetry](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-migration.html) and the [X-Ray SDK support timeline](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-daemon-timeline.html).

## Performance and Memory

Measure before optimizing. Compare duration, billed duration, memory use, CPU availability, network throughput, error rate, cold-start latency, concurrency, and cost.

- Reused SDK clients generally have negligible memory cost compared with application and dependency initialization.
- Right-size memory with representative load tests or production metrics.
- Add provisioned concurrency only when measured cold-start latency materially violates the service objective and the cost is justified.
- Add reserved concurrency to protect downstream systems or allocate account capacity, not as a generic performance toggle.
- Add caches or in-process concurrency only after identifying a bottleneck and defining lifecycle, correctness, and failure behavior.
- Move long-running waits and orchestration to Step Functions or event-driven workflows.

## Review Checklist

- [ ] Handler module and configured handler path agree
- [ ] Handler follows supporting functions and has an intentional context parameter
- [ ] Frequently used clients are reused; rare clients are lazy only when beneficial
- [ ] Business functions can receive clients for testing where useful
- [ ] Dry-run mode is trusted, validated, and suppresses every side effect
- [ ] Logs are structured, correlated, and free of complete sensitive events
- [ ] Powertools replaces meaningful code or supplies a required capability
- [ ] New tracing uses reviewed OpenTelemetry instrumentation
- [ ] Memory, concurrency, and cold-start changes are supported by measurements
