# Standard Library Modules

**Principle:** Prefer standard library modules over third-party alternatives when they meet your needs. This reduces dependencies, improves portability, and leverages well-tested, maintained code.

## File & Path Operations

**`pathlib` (Preferred over `os.path`):**

```python
# BAD: os.path (old-style, string-based)
import os
file_path = os.path.join("data", "users", "file.txt")
if os.path.exists(file_path):
    with open(file_path) as f:
        content = f.read()

# GOOD: pathlib (object-oriented, cross-platform)
from pathlib import Path

file_path = Path("data") / "users" / "file.txt"
if file_path.exists():
    content = file_path.read_text()

# Advanced pathlib features
base = Path("/data")
config_file = base / "config" / "app.yaml"
config_file.parent.mkdir(parents=True, exist_ok=True)
config_file.write_text("config: value")

# Iterate over directory
for py_file in Path("src").rglob("*.py"):
    print(py_file)

# Copy files/directories
import shutil
shutil.copy(source_path, dest_path)
shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

# Move/rename
source_path.rename(dest_path)

# Archive operations
import shutil
shutil.make_archive("backup", "zip", "data/")

# Disk usage
import shutil
total, used, free = shutil.disk_usage("/")
```

## Functional Programming

**`functools`:**

```python
from functools import wraps, cache, partial, singledispatch

# Preserve metadata in decorators
def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

# Cache function results
@cache
def expensive_computation(n: int) -> int:
    return sum(i * i for i in range(n))

# Pre-specify function arguments
multiply_by_two = partial(multiply, 2)

# Polymorphic functions based on type
@singledispatch
def process(data):
    raise NotImplementedError(f"Cannot process {type(data)}")

@process.register
def _(data: str):
    return data.upper()

@process.register
def _(data: int):
    return data * 2
```

## Data Structures & Algorithms

**`collections`, `heapq`, `graphlib`:**

```python
from collections import Counter, deque, defaultdict
import heapq
from graphlib import TopologicalSorter

# Counter for counting
word_counts = Counter(["a", "b", "a", "c", "a"])
# Counter({'a': 3, 'b': 1, 'c': 1})

# defaultdict
groups = defaultdict(list)
groups["team1"].append("Alice")

# deque (efficient append/pop from both ends)
queue = deque(maxlen=100)
queue.append(item)
queue.popleft()

# Min-heap (default)
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 2)
heapq.heappop(heap)  # Returns 2 (smallest)

# Max-heap (negate values)
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -2)
-largest = heapq.heappop(max_heap)  # Returns -5, so largest is 5

# Priority queue pattern
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass
class PriorityQueue:
    _queue: list[tuple[int, Any]] = field(default_factory=list)

    def push(self, priority: int, item: Any) -> None:
        heapq.heappush(self._queue, (priority, item))

    def pop(self) -> Any:
        return heapq.heappop(self._queue)[1]

# Build dependency graph
deps = {
    "task_a": ["task_b", "task_c"],
    "task_b": ["task_d"],
    "task_c": ["task_d"],
    "task_d": [],
}

# Get execution order
ts = TopologicalSorter(deps)
execution_order = list(ts.static_order())
# ['task_d', 'task_b', 'task_c', 'task_a']
```

## Security

**`secrets` (Use instead of `random` for security):**

```python
import secrets

# Generate secure random token
token = secrets.token_urlsafe(32)

# Generate secure random string
password = secrets.token_hex(16)

# Compare securely (constant-time)
secrets.compare_digest(provided_password, stored_password)

# BAD: Using random for security
import random
token = random.randint(1000, 9999)  # Not cryptographically secure!
```

## Configuration & Data Formats

**`tomllib` (Python 3.11+):**

```python
import tomllib

# Read TOML file
with open("config.toml", "rb") as f:
    config = tomllib.load(f)

# Access nested values
db_host = config["database"]["host"]

# BAD: Using third-party library
import tomli  # Unnecessary for Python 3.11+
```

**`json`:**

```python
import json

# Read JSON
with open("data.json") as f:
    data = json.load(f)

# Write JSON (with formatting)
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)

# Parse JSON string
data = json.loads(json_string)
```

## Utilities

**`itertools`:**

```python
from itertools import chain, pairwise, batched, cycle, groupby, combinations, permutations, product, zip_longest, islice

# Chain iterables
combined = chain(list1, list2, list3)

# Pairwise iteration (Python 3.10+)
for prev, curr in pairwise(items):
    process_pair(prev, curr)

# Batched (Python 3.12+)
for batch in batched(items, 100):
    process_batch(batch)

# Cycle through values
for item in cycle(["a", "b", "c"]):
    print(item)  # a, b, c, a, b, c, ...

# Group consecutive elements
for key, group in groupby([1, 1, 2, 2, 3]):
    print(key, list(group))

# Combinations and permutations
list(combinations([1, 2, 3], 2))  # [(1, 2), (1, 3), (2, 3)]
list(permutations([1, 2, 3], 2))  # [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

# Cartesian product
list(product([1, 2], [3, 4]))  # [(1, 3), (1, 4), (2, 3), (2, 4)]

# Zip longest (fill missing with default)
list(zip_longest([1, 2], [3], fillvalue=0))  # [(1, 3), (2, 0)]

# Slice iterator
for item in islice(range(100), 10, 20):  # Items 10-19
    print(item)
```

**`textwrap`:**

```python
from textwrap import wrap, fill, dedent, indent, shorten

# Wrap text to specified width
wrapped = wrap(long_text, width=50)

# Fill text (wrap and join)
filled = textwrap.fill(text, width=50)

# Dedent (remove leading whitespace) - great for SQL, templates
sql = textwrap.dedent("""
    SELECT *
    FROM users
    WHERE active = true
""").strip()

# Indent text
indented = textwrap.indent("Line 1\nLine 2", prefix="  ")

# Shorten text with ellipsis
short = textwrap.shorten("This is a very long string", width=20, placeholder="...")
```

**`contextlib` (Context managers):**

```python
from contextlib import contextmanager, suppress, redirect_stdout
import io

# Custom context manager
@contextmanager
def temporary_file():
    path = Path("/tmp/temp.txt")
    path.write_text("data")
    try:
        yield path
    finally:
        path.unlink()

# Suppress exceptions
with suppress(FileNotFoundError):
    Path("missing.txt").unlink()

# Redirect output
f = io.StringIO()
with redirect_stdout(f):
    print("This goes to StringIO")
output = f.getvalue()
```

**`dataclasses` (Data containers):**

```python
from dataclasses import dataclass, field, asdict

@dataclass
class User:
    name: str
    email: str
    age: int = 0
    tags: list[str] = field(default_factory=list)

user = User("John", "john@acme.com", 30)
user_dict = asdict(user)  # Convert to dict
```

**`enum` (Enumerations):**

```python
from enum import Enum, IntEnum, Flag

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

status = Status.ACTIVE
if status == Status.ACTIVE:
    print("Active!")

# IntEnum for integer values
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

# Flags for bitwise operations
class Permissions(Flag):
    READ = 1
    WRITE = 2
    EXECUTE = 4

perms = Permissions.READ | Permissions.WRITE
```

**`typing` (Type hints, Python 3.14+):**

```python
from typing import Annotated, Literal, Self, TypeAlias

# Type aliases
UserId: TypeAlias = int

# Literal types
Mode = Literal["dev", "staging", "prod"]

def deploy(env: Mode) -> None:
    ...

# Self type (Python 3.11+)
class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self

# Annotated (for metadata)
from typing import Annotated
Port = Annotated[int, "Port number between 1 and 65535"]
```

## When to Use Third-Party Libraries

**Use third-party libraries when:**

- Standard library doesn't provide the functionality
- Third-party library offers significant performance improvements
- Standard library solution is too complex for the use case
- You need features not available in stdlib

**Examples:**

- **`requests`** over `urllib` - Better API, connection pooling, sessions
- **`pydantic`** over `dataclasses` - Advanced validation, JSON schema
- **`click`** over `argparse` - Better CLI framework (if building complex CLIs)
- **`httpx`** over `urllib` - Async HTTP, HTTP/2 support

**Prefer stdlib when:**

- `pathlib` over `path.py`
- `tomllib` over `tomli` (Python 3.11+)
- `secrets` over `random` for security
- `json` over `ujson` (unless performance critical)
- `dataclasses` over `attrs` (for simple cases)
- `heapq` over `heapq` wrapper libraries
- `graphlib` over `networkx` (for simple topological sorting)
