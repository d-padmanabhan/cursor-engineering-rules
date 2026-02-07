# Async & Concurrency Patterns

## When to Use What

| Pattern | Use Case |
|---------|----------|
| **asyncio** | I/O-bound tasks (network, file I/O) |
| **threading** | I/O-bound with blocking libraries |
| **multiprocessing** | CPU-bound tasks |

## asyncio Basics

```python
import asyncio

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    # Run multiple coroutines concurrently
    results = await asyncio.gather(
        fetch_data("https://api.acme.com/users"),
        fetch_data("https://api.acme.com/products"),
    )
    return results

# Run the async main function
asyncio.run(main())
```

## Threading

```python
from concurrent.futures import ThreadPoolExecutor
import threading

def process_item(item: str) -> str:
    # Blocking I/O operation
    return item.upper()

# Using ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_item, items))

# Thread-safe operations
lock = threading.Lock()
with lock:
    shared_resource.update()
```

## Multiprocessing

```python
from multiprocessing import Pool, cpu_count

def cpu_intensive_task(n: int) -> int:
    return sum(range(n))

# Use for CPU-bound tasks
with Pool(processes=cpu_count()) as pool:
    results = pool.map(cpu_intensive_task, [1000000, 2000000, 3000000])
```

## Session Reuse

```python
import requests

# Reuse session for multiple requests (connection pooling)
session = requests.Session()
session.headers.update({"Authorization": "Bearer token"})

for url in urls:
    response = session.get(url)
    process(response)
```

## Generators for Memory Efficiency

```python
def read_large_file(filepath: str):
    """Yield lines one at a time instead of loading entire file."""
    with open(filepath) as f:
        for line in f:
            yield line.strip()

# Process line by line
for line in read_large_file("large_data.txt"):
    process(line)
```

## Retry with Exponential Backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=10)
)
def fetch_with_retry(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

## Custom Retry Decorator

```python
import functools
import time

def retry(max_attempts: int = 3, base_delay: float = 0.2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempt >= max_attempts:
                        raise
                    time.sleep(delay)
                    delay = min(delay * 2, 2.0)
                    attempt += 1
        return wrapper
    return decorator
```

## Performance Profiling

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()
result = expensive_function()
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)  # Top 10 functions
```

## Efficient Data Structures

```python
# Set for O(1) lookups
allowed_ids = {"id1", "id2", "id3"}
if user_id in allowed_ids:
    allow()

# heapq for priority queues
import heapq
heap = []
heapq.heappush(heap, (priority, item))
_, item = heapq.heappop(heap)

# bisect for sorted list operations
import bisect
sorted_list = [1, 3, 5, 7, 9]
bisect.insort(sorted_list, 4)  # [1, 3, 4, 5, 7, 9]
```
