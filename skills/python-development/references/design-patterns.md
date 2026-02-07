# Design Patterns

Design patterns provide reusable solutions to common problems. Use them where they add clarity and maintainability - avoid forcing patterns where simple code suffices.

## Decorator Pattern (Advanced)

**Function Decorators:**

```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')

def retry(max_attempts: int = 3):
    """Decorator that retries function on failure."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(f"Attempt {attempt} failed: {e}, retrying...")
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
        return wrapper
    return decorator

@retry(max_attempts=5)
def fetch_data(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

**Class Decorators:**

```python
def add_logging(cls):
    """Class decorator that adds logging to all methods."""
    for name, method in vars(cls).items():
        if callable(method) and not name.startswith('_'):
            setattr(cls, name, log_method(method))
    return cls

def log_method(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(self, *args, **kwargs)
        logger.info(f"{func.__name__} returned {result}")
        return result
    return wrapper

@add_logging
class DataProcessor:
    def process(self, data: list[int]) -> int:
        return sum(data)
```

**Property Decorators:**

```python
class CachedProperty:
    """Descriptor that caches property value."""
    def __init__(self, func: Callable[[object], T]):
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__

    def __set_name__(self, owner: type, name: str):
        self.attrname = f"_{name}"

    def __get__(self, obj: object, objtype: type | None = None) -> T:
        if obj is None:
            return self
        if not hasattr(obj, self.attrname):
            setattr(obj, self.attrname, self.func(obj))
        return getattr(obj, self.attrname)

class ExpensiveComputation:
    @CachedProperty
    def result(self) -> int:
        """Expensive computation cached after first access."""
        print("Computing...")
        return sum(i * i for i in range(1000000))
```

## Factory Method Pattern

Creates objects without specifying their exact class. Useful when object creation logic is complex or varies based on input.

```python
from typing import Protocol

class DatabaseConnection(Protocol):
    """Protocol for database connections."""
    def execute(self, query: str) -> list[dict]: ...

class PostgresConnection:
    def execute(self, query: str) -> list[dict]:
        return [{"result": "postgres_data"}]

class MySQLConnection:
    def execute(self, query: str) -> list[dict]:
        return [{"result": "mysql_data"}]

class DatabaseFactory:
    """Factory for creating database connections."""
    @staticmethod
    def create_connection(db_type: str) -> DatabaseConnection:
        match db_type.lower():
            case "postgres": return PostgresConnection()
            case "mysql": return MySQLConnection()
            case _: raise ValueError(f"Unsupported: {db_type}")
```

## Singleton Pattern

Ensures a class has only one instance. Useful for managing shared resources like boto3 clients, database connections, or configuration objects.

```python
from typing import Any

class SingletonMeta(type):
    """Metaclass that creates a Singleton base class."""
    _instances: dict[type, object] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class AWSClientManager(metaclass=SingletonMeta):
    """Singleton manager for AWS boto3 clients."""
    def __init__(self) -> None:
        self._clients: dict[str, Any] = {}

    def get_client(self, service: str, region: str = "us-east-1") -> Any:
        key = f"{service}:{region}"
        if key not in self._clients:
            self._clients[key] = boto3.client(service, region_name=region)
        return self._clients[key]

# Usage in Lambda or application code
aws_clients = AWSClientManager()
s3_client = aws_clients.get_client("s3", "us-east-1")
```

## Strategy Pattern

Defines a family of interchangeable algorithms. Useful for multi-region AWS operations or varying behaviors based on environment.

```python
from typing import Protocol

class DeploymentStrategy(Protocol):
    def deploy(self, application: str) -> None: ...

class DevelopmentDeployment:
    def deploy(self, application: str) -> None:
        print(f"Deploying {application} to dev (single instance)")

class ProductionDeployment:
    def deploy(self, application: str) -> None:
        print(f"Deploying {application} to prod (multi-AZ, auto-scaling)")

class DeploymentContext:
    def __init__(self, strategy: DeploymentStrategy) -> None:
        self._strategy = strategy

    def execute_deployment(self, application: str) -> None:
        self._strategy.deploy(application)
```
