# AWS & Boto3 Best Practices

## Client Configuration

**Global Initialization:** In Lambda, create `boto3` clients globally (outside handler) to reuse across invocations:

```python
import boto3
from botocore.config import Config

boto_config = Config(
    retries={"max_attempts": 5, "mode": "standard"},
    connect_timeout=5,
    read_timeout=30
)

s3_client = boto3.client("s3", config=boto_config, region_name="us-east-1")
```

**Region Handling:** Retrieve from `AWS_REGION` env var, default to `us-east-1`, allow override via parameter.

**Client Factory:** Create reusable factory function:

```python
def create_boto3_client(service_name: str, region_name: str, **kwargs) -> boto3.client:
    try:
        config = Config(retries={"max_attempts": 5, "mode": "standard"})
        client = boto3.client(service_name, region_name=region_name, config=config, **kwargs)
        logger.info(f"Created boto3 client for {service_name} in {region_name}")
        return client
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to create boto3 client: {e}")
        raise
```

## Error Handling

**Specific Exceptions:** Catch `botocore.exceptions.ClientError`, `ResourceNotFoundError`, etc.

**Error Codes:** Check `e.response['Error']['Code']` for specific AWS errors.

```python
from botocore.exceptions import ClientError

try:
    response = s3_client.get_object(Bucket="my-bucket", Key="my-key")
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'NoSuchKey':
        logger.warning("Object not found")
    elif error_code == 'AccessDenied':
        logger.error("Access denied")
    else:
        raise
```

## Pagination & Waiters

**Paginators:** Use for large result sets:

```python
paginator = s3_client.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="my-bucket"):
    for obj in page.get("Contents", []):
        process(obj)
```

**NextToken:** Handle manually if paginator unavailable.

**Waiters:** Pause until resource is ready:

```python
waiter = ec2_client.get_waiter("instance_running")
waiter.wait(InstanceIds=["i-123456"])
```

## Lambda Patterns

**Global Scope Pattern (Recommended):**

```python
import boto3
import os
from botocore.config import Config

#  CORRECT: Create clients in global scope (outside handler)
boto_config = Config(
    retries={"max_attempts": 10, "mode": "adaptive"},
    connect_timeout=5,
    read_timeout=30,
)

region = os.environ["AWS_REGION"]
s3_client = boto3.client("s3", config=boto_config, region_name=region)
dynamodb_client = boto3.client("dynamodb", config=boto_config, region_name=region)

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda handler reuses clients from global scope."""
    response = s3_client.list_buckets()
    return {"statusCode": 200, "body": "Success"}
```

**Anti-Patterns:**

```python
#  WRONG: Creates new client on every invocation (cold start penalty)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    s3_client = boto3.client("s3")  # Bad: Recreated every time
    return {"statusCode": 200}

#  WRONG: Ties client lifecycle to class instance
class S3Manager:
    def __init__(self):
        self.s3_client = boto3.client("s3")  # Bad
```

**Cold Start Optimization:**

```python
#  Lazy initialization for rarely-used clients
_sns_client: Any = None

def get_sns_client() -> Any:
    """Lazy-load SNS client only when needed."""
    global _sns_client
    if _sns_client is None:
        _sns_client = boto3.client("sns")
    return _sns_client

#  Always-needed clients in global scope
s3_client = boto3.client("s3")  # Frequently used

def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    s3_client.list_buckets()  # Always available

    if event.get("notify"):
        sns = get_sns_client()  # Loaded only if needed
        sns.publish(TopicArn="...", Message="...")

    return {"statusCode": 200}
```

**AWS Lambda Powertools (Observability):**

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
    result = process_items(event["items"])
    return {"statusCode": 200, "body": result}

@tracer.capture_method
def process_items(items: list[str]) -> str:
    """Process items with automatic tracing."""
    logger.info(f"Processing {len(items)} items")
    return "success"
```

## Region Validation

```python
ALLOWED_REGIONS = {"us-east-1", "us-west-2", "eu-west-1"}

def get_aws_region() -> str:
    """Get AWS region from environment or default."""
    region = os.getenv("AWS_REGION", "us-east-1")
    
    if region not in ALLOWED_REGIONS:
        raise ValueError(f"Region {region} not in allowed list: {ALLOWED_REGIONS}")
    
    return region
```
