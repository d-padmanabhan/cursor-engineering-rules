# Performance Optimization

**Golden Rule:** Profile first, optimize second. Measure before optimizing.

## Profiling

**Profiling:** Use `cProfile`, `line_profiler`, or `memory_profiler` to identify bottlenecks.

```python
import cProfile
import pstats

def profile_function():
    """Profile function execution."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    result = expensive_operation()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

    return result

# Command-line profiling
# python -m cProfile -o profile.stats script.py
# python -m pstats profile.stats
```

## Performance Optimization Examples

**String Concatenation:**

```python
# BAD: O(n²) - creates new string each iteration
result = ""
for item in items:
    result += item

# GOOD: O(n) - uses list and join
result = "".join(items)

# GOOD: For complex formatting
parts = [f"{key}={value}" for key, value in data.items()]
result = "&".join(parts)
```

**List Comprehensions vs Loops:**

```python
# BAD: Slower, more verbose
result = []
for x in range(1000):
    if x % 2 == 0:
        result.append(x * 2)

# GOOD: Faster, more Pythonic
result = [x * 2 for x in range(1000) if x % 2 == 0]

# For complex logic, generator expressions save memory
result = (x * 2 for x in range(1000000) if x % 2 == 0)  # Lazy evaluation
```

**Dictionary Lookups:**

```python
# BAD: Multiple lookups
if key in data:
    value = data[key]
    process(value)

# GOOD: Single lookup with default
value = data.get(key)
if value is not None:
    process(value)

# GOOD: Using try/except for rare KeyError (faster when key exists)
try:
    value = data[key]
    process(value)
except KeyError:
    pass
```

**Memory-Efficient Iteration:**

```python
# BAD: Loads all into memory
with open("large_file.txt") as f:
    lines = f.readlines()  # Loads entire file
    for line in lines:
        process(line)

# GOOD: Iterates line by line
with open("large_file.txt") as f:
    for line in f:  # Generator, memory efficient
        process(line)

# GOOD: Using generators for large datasets
def process_large_dataset(items):
    """Process items one at a time."""
    for item in items:
        yield transform(item)  # Lazy evaluation

# Process without loading all into memory
for result in process_large_dataset(huge_list):
    save(result)
```

**Caching Expensive Operations:**

```python
from functools import lru_cache

# GOOD: Cache function results
@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """Expensive computation cached by input."""
    # Complex calculation
    return sum(i * i for i in range(n))

# GOOD: Custom caching with TTL
from functools import wraps
import time

def cached_with_ttl(ttl_seconds: int):
    """Cache decorator with time-to-live."""
    cache: dict[tuple, tuple[float, any]] = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            if key in cache:
                cached_time, cached_value = cache[key]
                if now - cached_time < ttl_seconds:
                    return cached_value

            result = func(*args, **kwargs)
            cache[key] = (now, result)
            return result
        return wrapper
    return decorator

@cached_with_ttl(ttl_seconds=300)
def fetch_data(url: str) -> dict:
    return requests.get(url).json()
```

**Pre-allocation:**

```python
# BAD: Grows list dynamically
result = []
for i in range(1000):
    result.append(i * 2)

# GOOD: Pre-allocate when size is known
result = [0] * 1000
for i in range(1000):
    result[i] = i * 2

# GOOD: Pre-allocate with list comprehension (fastest)
result = [i * 2 for i in range(1000)]
```

**Using Built-in Functions:**

```python
# BAD: Manual implementation
total = 0
for item in items:
    total += item

# GOOD: Built-in is faster
total = sum(items)

# BAD: Manual max
max_val = items[0]
for item in items[1:]:
    if item > max_val:
        max_val = item

# GOOD: Built-in
max_val = max(items)
```

## Session Reuse

**Session Reuse:** Use `requests.Session()` for multiple API calls.

```python
import requests

# BAD: New connection for each request
for url in urls:
    response = requests.get(url)  # New connection each time
    process(response.json())

# GOOD: Reuse session
session = requests.Session()
for url in urls:
    response = session.get(url)  # Reuses connection
    process(response.json())
```

## Concurrency Decision Guide

**When to Use Each Concurrency Model:**

- **`asyncio`:** For I/O-bound tasks with async libraries
- **`threading`:** For I/O-bound with blocking libraries
- **`multiprocessing`:** For CPU-bound tasks

See [async-concurrency.md](async-concurrency.md) for detailed patterns.

## Speed Boosts

**Speed Boosts:** Use `numba` (NumPy-focused), `cython` (C extensions), or `codon` (`@codon.jit` for general Python) for performance-critical code. Codon has fewer restrictions than Numba but isn't a full CPython drop-in. Profile first.

## Efficient Lookups

**Efficient Lookups:** Use `set` for O(1) lookups, `heapq` for priority queues, `bisect` for sorted lists.

```python
import bisect

# BAD: Linear search in sorted list
def find_position(items: list[int], value: int) -> int:
    for i, item in enumerate(items):
        if item >= value:
            return i
    return len(items)

# GOOD: Binary search with bisect
def find_position(items: list[int], value: int) -> int:
    return bisect.bisect_left(items, value)
```

## Parallel Computing

**Parallel Computing:** Use `ray` or `dask` for distributed workloads if needed.

## Complexity Analysis

**Complexity Analysis:** Avoid O(n²) loops - refactor with better data structures.

```python
# BAD: O(n²) - nested loops
def find_pairs(items: list[int], target: int) -> list[tuple[int, int]]:
    pairs = []
    for i, a in enumerate(items):
        for j, b in enumerate(items[i+1:], i+1):
            if a + b == target:
                pairs.append((a, b))
    return pairs

# GOOD: O(n) - single pass with set
def find_pairs(items: list[int], target: int) -> list[tuple[int, int]]:
    seen = set()
    pairs = []
    for item in items:
        complement = target - item
        if complement in seen:
            pairs.append((complement, item))
        seen.add(item)
    return pairs
```
