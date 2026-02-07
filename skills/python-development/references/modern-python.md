# Modern Python Features

## Core Language Features

### f-strings

```python
name = "Alice"
print(f"User: {name}")
print(f"{name!r}")  # Python 3.12: debug repr
```

### match-case (Python 3.10+)

```python
def handle_response(code: int) -> str:
    match code:
        case 200: return "Success"
        case 400 | 404: return "Client Error"
        case _: return "Unknown"
```

### Walrus Operator (:=)

```python
if (count := len(items)) > 5:
    print(f"Processing {count} items")
```

### Comprehensions

```python
# List comprehension
doubled = [x * 2 for x in numbers]

# Dict comprehension
squared = {x: x**2 for x in range(5)}

# Generator expression (memory efficient)
total = sum(x * 2 for x in numbers)
```

## Dataclasses

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    product_id: int
    name: str
    tags: list[str] = field(default_factory=list)

@dataclass(slots=True, frozen=True)
class ImmutableConfig:
    host: str
    port: int = 8080
```

## Functional Programming

### functools.cache

```python
from functools import cache

@cache
def expensive_calculation(n: int) -> int:
    return sum(range(n))
```

### functools.partial

```python
from functools import partial

def multiply(x: int, y: int) -> int:
    return x * y

double = partial(multiply, 2)
```

### functools.singledispatch

```python
from functools import singledispatch

@singledispatch
def process(data):
    raise NotImplementedError

@process.register(str)
def _(data: str) -> str:
    return data.upper()

@process.register(list)
def _(data: list) -> int:
    return len(data)
```

## Collections

```python
from collections import Counter, defaultdict, deque

# Counter
word_counts = Counter(["a", "b", "a", "c", "a"])
# Counter({'a': 3, 'b': 1, 'c': 1})

# defaultdict
groups = defaultdict(list)
groups["team1"].append("Alice")

# deque (efficient append/pop from both ends)
queue = deque(maxlen=100)
queue.append(item)
queue.popleft()
```

## Context Managers

```python
from contextlib import contextmanager

@contextmanager
def database_connection(db_name: str):
    logger.info(f"Connecting to {db_name}")
    conn = create_connection(db_name)
    try:
        yield conn
    finally:
        conn.close()
        logger.info("Disconnected")

# Usage
with database_connection("mydb") as conn:
    conn.execute("SELECT * FROM users")
```

## Protocols (Structural Typing)

```python
from typing import Protocol

class Writable(Protocol):
    def write(self, data: str) -> None: ...

def save_data(writer: Writable, data: str) -> None:
    writer.write(data)

# Any object with a write method will work
```

## Abstract Base Classes

```python
from abc import ABC, abstractmethod

class DataWriter(ABC):
    @abstractmethod
    def write(self, data: str) -> None:
        ...
    
    def log(self, message: str) -> None:
        print(f"[LOG] {message}")

class FileWriter(DataWriter):
    def write(self, data: str) -> None:
        with open("output.txt", "w") as f:
            f.write(data)
```

## Design Patterns

### Factory Pattern

```python
class DatabaseFactory:
    @staticmethod
    def create_connection(db_type: str) -> DatabaseConnection:
        match db_type.lower():
            case "postgres": return PostgresConnection()
            case "mysql": return MySQLConnection()
            case _: raise ValueError(f"Unsupported: {db_type}")
```

### Singleton Pattern

```python
class SingletonMeta(type):
    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.settings = {}
```

### Strategy Pattern

```python
from typing import Protocol

class DeploymentStrategy(Protocol):
    def deploy(self, app: str) -> None: ...

class DevDeployment:
    def deploy(self, app: str) -> None:
        print(f"Deploying {app} to dev")

class ProdDeployment:
    def deploy(self, app: str) -> None:
        print(f"Deploying {app} to prod (multi-AZ)")

class Deployer:
    def __init__(self, strategy: DeploymentStrategy):
        self.strategy = strategy
    
    def execute(self, app: str) -> None:
        self.strategy.deploy(app)
```

## Text Processing

```python
from textwrap import dedent

query = dedent("""
    SELECT * FROM users
    WHERE age > 18
    ORDER BY name
""").strip()
```

## Timestamps

```python
from datetime import datetime, timezone

# Always use UTC-aware timestamps
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
```
