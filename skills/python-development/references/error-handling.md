# Error Handling & Resilience

## Domain Boundary Exception Handling

Catch the specific failures a boundary can translate. Preserve causal context and never swallow errors by returning empty/default data.

```python
#  BAD: Masks failure and returns empty data
def load_database() -> dict:
    try:
        # Load database data...
        return data
    except OSError as error:
        logger.error("Unable to read database", exc_info=True)
        return {"books": [], "library": []}  # BAD! Silent failure

# GOOD: Re-raises the expected failure with context and fails fast
def load_database() -> dict:
    try:
        # Load database data...
        return data
    except OSError as error:
        raise RuntimeError("Failed to load database") from error
```

Catch `Exception` only at an intentional process, request, worker, or task boundary that must log an unexpected failure before terminating or returning a safe error. Use `logger.exception(...)`, then re-raise or translate. Do not continue normal processing.

## Exception Groups

**Exception Groups:** For batch operations:

```python
errors: list[Exception] = []
for item in items:
    try:
        process(item)
    except ProcessingError as error:
        errors.append(error)
if errors:
    raise ExceptionGroup("Batch failed", errors)
```

## Retry Libraries

**Retry Libraries:** Use `tenacity`, `backoff`, or `retrying` for transient failures:

```python
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

@retry(
    retry=retry_if_exception_type(TransientApiError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10),
)
def fetch_data() -> dict:
    response = requests.get("https://api.acme.com/data")
    response.raise_for_status()
    return response.json()
```

Retry only failures known to be transient, and only when the operation is idempotent or otherwise retry-safe. Bound attempts and elapsed time; do not hide permanent validation, authorization, or programming errors behind retries.

## Custom Exceptions

**Custom Exceptions:** Define domain-specific exceptions for clarity.

```python
class FileProcessingError(Exception):
    """Base exception for file processing errors."""
    pass

class SourceFileNotFoundError(FileProcessingError):
    """File not found error."""
    pass

class FileFormatError(FileProcessingError):
    """Invalid file format error."""
    pass

class FilePermissionError(FileProcessingError):
    """File permission error."""
    pass

# Usage
def process_file(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise SourceFileNotFoundError(f"File not found: {file_path}")

    try:
        return parse_file(file_path)
    except ValueError as error:
        raise FileFormatError(f"Invalid file format: {error}") from error
```

## Warnings Module

**Warnings Module:** Use for non-critical issues:

```python
import warnings

# Deprecation warning
def old_function():
    warnings.warn(
        "old_function is deprecated. Use new_function instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()

# Runtime warning
if len(data) > 10000:
    warnings.warn(
        "Large dataset detected. Processing may be slow.",
        RuntimeWarning
    )
```

## Error Context

**Adding Context to Exceptions:**

```python
def process_user_data(user_id: str, data: dict) -> dict:
    try:
        validate_data(data)
        return transform_data(data)
    except ValueError as error:
        raise ValueError(
            f"Invalid data for user {user_id}: {error}"
        ) from error
```
