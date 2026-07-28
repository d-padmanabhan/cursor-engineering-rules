# AWS and Boto3 Best Practices

This is the canonical SDK reference for Python code that calls AWS services. Lambda-specific lifecycle and observability guidance lives in [AWS Lambda](aws-lambda.md).

## Client Lifecycle

Reuse clients when calls share the same service, region, credentials, and configuration. In Lambda, create frequently used clients at module scope so warm invocations reuse their connection pools. Create a client per request only when its configuration must vary per request.

```python
import boto3
from botocore.client import BaseClient
from botocore.config import Config

_BOTO_CONFIG = Config(
    retries={
        "mode": "standard",
        "total_max_attempts": 5,
    },
    connect_timeout=3,
    read_timeout=10,
)

s3_client: BaseClient = boto3.client("s3", config=_BOTO_CONFIG)
```

Pass clients into business functions when doing so makes dependencies and tests clearer. A client owned by a class is also valid when the class instance is reused for the intended lifetime.

Use `functools.cache` or a bounded cache only when clients genuinely vary by stable configuration such as region. Do not add singleton managers or unbounded dictionaries for one fixed client.

```python
from functools import cache


@cache
def get_ec2_client(region_name: str) -> BaseClient:
    """Return a reusable EC2 client for a validated region."""
    return boto3.client(
        "ec2",
        region_name=region_name,
        config=_BOTO_CONFIG,
    )
```

## Retries and Timeouts

- Prefer Botocore's `standard` retry mode for transient AWS failures.
- Use `total_max_attempts` when configuring a `Config` object. It includes the initial request; `max_attempts` in `Config` counts only retries.
- Size retry attempts, connection timeout, and read timeout to fit inside the caller's end-to-end deadline.
- Do not wrap an SDK call in another retry loop unless the higher-level operation is idempotent and needs recovery beyond Botocore's request retries.
- Treat `adaptive` mode as an intentional, tested choice. Boto3 currently documents it as experimental.

See the official [Botocore Config reference](https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html) and [Boto3 retry guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html).

## Region Configuration

Use the SDK's default region resolution when the client should operate in the workload's execution region. Lambda supplies `AWS_REGION`, and the default credential/configuration chain already uses it.

Require and validate explicit configuration when a client must target a different or authoritative region. Do not silently default to `us-east-1`; a fallback can send data or mutations to the wrong region.

```python
import os


def require_region(variable_name: str) -> str:
    """Return a required region setting."""
    region = os.getenv(variable_name)
    if not region:
        raise ValueError(f"{variable_name} environment variable is required")
    return region
```

Use an allowlist only when the application has an actual regional policy. Keep the allowlist in configuration rather than embedding a generic list in shared helpers.

## Error Handling

Catch `botocore.exceptions.ClientError` only when the caller can recover, translate the failure, or change behavior based on the AWS service error code. There is no general `botocore.exceptions.ResourceNotFoundError`; inspect `exc.response["Error"]["Code"]` or use a service-specific exception exposed through `client.exceptions`.

```python
from botocore.exceptions import ClientError


def describe_instance(ec2_client: BaseClient, instance_id: str) -> dict[str, object]:
    """Return an EC2 instance description."""
    try:
        return ec2_client.describe_instances(InstanceIds=[instance_id])
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "InvalidInstanceID.NotFound":
            raise ValueError(f"EC2 instance {instance_id} was not found") from exc
        raise
```

Do not catch, log, and re-raise every SDK exception; that creates duplicate logs without adding recovery. At an operational boundary, log safe identifiers and the error code, not credentials, authorization headers, secret values, request bodies, or sensitive service responses.

## Pagination

Use a paginator when the operation supports one, and stream items page by page unless the complete result set is genuinely required in memory.

```python
from collections.abc import Iterator


def iter_s3_objects(s3_client: BaseClient, bucket_name: str) -> Iterator[dict[str, object]]:
    """Yield S3 objects without accumulating every page."""
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name):
        yield from page.get("Contents", [])
```

If no paginator exists, loop on the continuation field returned by that operation. Continuation fields are service-specific, including `NextToken`, `Marker`, `ContinuationToken`, and DynamoDB's `LastEvaluatedKey`.

```python
def iter_table_items(dynamodb_client: BaseClient, table_name: str) -> Iterator[dict[str, object]]:
    """Yield DynamoDB items using the service continuation key."""
    exclusive_start_key: dict[str, object] | None = None

    while True:
        request: dict[str, object] = {"TableName": table_name}
        if exclusive_start_key:
            request["ExclusiveStartKey"] = exclusive_start_key

        response = dynamodb_client.scan(**request)
        yield from response.get("Items", [])

        exclusive_start_key = response.get("LastEvaluatedKey")
        if not exclusive_start_key:
            return
```

## Waiters

Use a waiter only when a subsequent operation requires a resource to reach a particular state. Always bound its delay and attempts to the caller's deadline.

```python
waiter = ec2_client.get_waiter("instance_running")
waiter.wait(
    InstanceIds=[instance_id],
    WaiterConfig={
        "Delay": 5,
        "MaxAttempts": 12,
    },
)
```

Do not hold a Lambda invocation open for long-running provisioning. Prefer event-driven completion, Step Functions, or another durable orchestration mechanism.

## Review Checklist

- [ ] Frequently used clients are reused at the appropriate lifetime
- [ ] Client caches are necessary, keyed by bounded validated values, and not speculative
- [ ] `standard` retries and `total_max_attempts` fit the caller's deadline
- [ ] Cross-region clients require explicit validated configuration
- [ ] `ClientError` handling checks service error codes and preserves exception chains
- [ ] Logs exclude credentials, secrets, authorization data, and sensitive responses
- [ ] Paginated results stream unless full accumulation is required
- [ ] Waiters have bounded `Delay` and `MaxAttempts`
