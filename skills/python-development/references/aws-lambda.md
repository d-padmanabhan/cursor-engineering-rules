# AWS Lambda & Boto3 Patterns

## Global Scope Pattern (Required)

Create boto3 clients in global scope to reuse across invocations:

```python
import boto3
import os
from botocore.config import Config
from typing import Any

# CORRECT: Create clients in global scope
boto_config = Config(
    retries={"max_attempts": 10, "mode": "adaptive"},
    connect_timeout=5,
    read_timeout=30,
)

region = os.environ.get("AWS_REGION", "us-east-1")
s3_client = boto3.client("s3", config=boto_config, region_name=region)
dynamodb_client = boto3.client("dynamodb", config=boto_config, region_name=region)

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler reuses clients from global scope."""
    response = s3_client.list_buckets()
    return {"statusCode": 200, "body": "Success"}
```

## Anti-Patterns to Avoid

```python
# WRONG: Creates new client on every invocation
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    s3_client = boto3.client("s3")  # Bad: Cold start penalty
    return {"statusCode": 200}

# WRONG: Client in class instance
class S3Manager:
    def __init__(self):
        self.s3_client = boto3.client("s3")  # Bad: Tied to instance
```

## Lazy Initialization for Rarely-Used Clients

```python
_sns_client: Any = None

def get_sns_client() -> Any:
    """Lazy-load SNS client only when needed."""
    global _sns_client
    if _sns_client is None:
        _sns_client = boto3.client("sns")
    return _sns_client

# Always-needed clients in global scope
s3_client = boto3.client("s3")  # Frequently used

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    s3_client.list_buckets()  # Always available

    if event.get("notify"):
        sns = get_sns_client()  # Loaded only if needed
        sns.publish(TopicArn="...", Message="...")

    return {"statusCode": 200}
```

## AWS Lambda Powertools

```python
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from typing import Any

logger = Logger()
tracer = Tracer()
metrics = Metrics()

@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler with full observability."""
    logger.info("Processing request", extra={"request_id": event.get("requestId")})
    metrics.add_metric(name="ItemsProcessed", unit=MetricUnit.Count, value=10)
    return {"statusCode": 200, "body": "Success"}
```

## Error Handling

```python
from botocore.exceptions import ClientError, BotoCoreError

def get_object_safe(bucket: str, key: str) -> bytes | None:
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchKey":
            logger.warning(f"Key not found: {key}")
            return None
        elif error_code == "AccessDenied":
            logger.error(f"Access denied to {bucket}/{key}")
            raise
        else:
            raise
```

## Pagination

```python
def list_all_objects(bucket: str) -> list[dict]:
    """Use paginator for large result sets."""
    paginator = s3_client.get_paginator("list_objects_v2")
    objects = []
    
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            objects.append(obj)
    
    return objects
```

## Waiters

```python
def wait_for_instance(instance_id: str) -> None:
    """Wait until instance is running."""
    waiter = ec2_client.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])
    logger.info(f"Instance {instance_id} is now running")
```

## Region Validation

```python
ALLOWED_REGIONS = [
    "us-east-1", "us-west-2", "us-east-2", "ca-central-1",
    "eu-west-1", "eu-west-2", "eu-central-1", "eu-north-1",
    "ap-southeast-1", "ap-southeast-2"
]

def validate_region(region: str) -> str:
    if region not in ALLOWED_REGIONS:
        raise ValueError(f"Invalid region: {region}. Allowed: {ALLOWED_REGIONS}")
    return region
```

## Client Factory

```python
def create_boto3_client(
    service_name: str,
    region_name: str = "us-east-1",
    **kwargs
) -> Any:
    """Create boto3 client with standard configuration."""
    try:
        config = Config(
            retries={"max_attempts": 5, "mode": "standard"},
            connect_timeout=5,
            read_timeout=30
        )
        client = boto3.client(
            service_name,
            region_name=validate_region(region_name),
            config=config,
            **kwargs
        )
        logger.info(f"Created boto3 client for {service_name} in {region_name}")
        return client
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to create boto3 client: {e}")
        raise
```

## Lambda Best Practices Checklist

- [ ] Clients in global scope (not in handler)
- [ ] AWS Lambda Powertools for observability
- [ ] Specific exception handling (`ClientError` codes)
- [ ] Paginators for large result sets
- [ ] Lazy initialization for rarely-used clients
- [ ] Handler at end of file
- [ ] Use `context.aws_request_id` for correlation
- [ ] Never log credentials or session tokens
- [ ] Dry-run mode for testing
- [ ] Pass clients to functions as parameters
