# Logging & Observability

## Logger Setup

**Setup:** Use a custom logger setup function at the start of scripts.

**Pattern:**

```python
import logging
import time

def setup_custom_logger(name: str) -> logging.Logger:
    """Create and configure a logger with UTC timestamps."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    class UTCFormatter(logging.Formatter):
        converter = time.gmtime

    formatter = UTCFormatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%c %Z"
    )

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_custom_logger(__name__)
```

## Structured Logging

**Structured Logging:** Use `loguru` or JSON format for observability pipelines where needed.

**Error Logging:** Include `exc_info=True` for tracebacks: `logger.error("Error", exc_info=True)`.

```python
import logging
import json

# JSON formatter for structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data)

# Configure JSON logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Usage with extra context
logger.info("User action", extra={
    "user_id": user_id,
    "action": "login",
    "ip_address": ip_address,
})
```

## Log Levels

**Log Levels:**

```python
logger.debug("Detailed debug information")
logger.info("General informational message")
logger.warning("Warning message - recoverable issue")
logger.error("Error message - needs attention", exc_info=True)
logger.critical("Critical error - system may be unstable")
```

**Conditional Debug Output:**

```python
import os
import logging

DEBUG = os.getenv("DEBUG", "0") == "1"

def debug_print(message: str):
    """Print only when DEBUG is enabled."""
    if DEBUG:
        print(f"[DEBUG] {message}")

# Or use logging levels
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
```
