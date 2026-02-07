# Error Handling & Resilience

## Domain Boundary Exception Handling

**Domain Boundary Exception Handling:** Always re-raise exceptions with context at system boundaries. Never swallow errors by returning empty/default data.

```python
#  BAD: Masks failure and returns empty data
def load_database() -> dict:
    try:
        # Load database data...
        return data
    except Exception as e:
        logger.error(f"Error loading YAML database: {str(e)}")
        return {"books": [], "library": []}  # BAD! Silent failure

#  GOOD: Re-raises with context, fails fast
def load_database() -> dict:
    try:
        # Load database data...
        return data
    except Exception as e:
        logger.error(f"Error loading YAML database: {str(e)}")
        raise RuntimeError(f"Failed to load database: {str(e)}") from e
```

## Exception Groups

**Exception Groups:** For batch operations:

```python
from exceptiongroup import ExceptionGroup

errors = []
for item in items:
    try:
        process(item)
    except Exception as e:
        errors.append(e)
if errors:
    raise ExceptionGroup("Batch failed", errors)
```

## Retry Libraries

**Retry Libraries:** Use `tenacity`, `backoff`, or `retrying` for transient failures:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def fetch_data() -> dict:
    response = requests.get("https://api.acme.com/data")
    response.raise_for_status()
    return response.json()
```

**Custom Retry with Context:**

```python
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(max_attempts: int = 3, initial_delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            
            raise last_exception
        return wrapper
    return decorator

@retry_with_backoff(max_attempts=5, initial_delay=1.0)
def unreliable_operation():
    # Operation that may fail transiently
    pass
```

## Custom Exceptions

**Custom Exceptions:** Define domain-specific exceptions for clarity.

```python
class FileProcessingError(Exception):
    """Base exception for file processing errors."""
    pass

class FileNotFoundError(FileProcessingError):
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
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        return parse_file(file_path)
    except ValueError as e:
        raise FileFormatError(f"Invalid file format: {e}") from e
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
    except ValueError as e:
        raise ValueError(
            f"Invalid data for user {user_id}: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Failed to process data for user {user_id}: {e}"
        ) from e
```
