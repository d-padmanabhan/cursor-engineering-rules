# Async & Concurrency Patterns

## When to Use What

| Pattern | Use Case |
|---------|----------|
| **asyncio** | High-concurrency I/O with async-compatible libraries |
| **threading** | I/O-bound with blocking libraries |
| **process pool / multiprocessing** | Measured CPU-bound work that benefits after serialization overhead |
| **sequential code** | Default when concurrency does not provide measured value |

Ordinary file operations remain blocking unless they are delegated to a thread or use a platform-specific async implementation.

## Structured asyncio

Reuse clients, bound concurrency, set deadlines, and let cancellation propagate. `TaskGroup` cancels sibling tasks when one fails and waits for their cleanup.

```python
import asyncio

import aiohttp


async def fetch_data(
    session: aiohttp.ClientSession,
    limiter: asyncio.Semaphore,
    url: str,
) -> dict[str, object]:
    async with limiter:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()


async def fetch_all(urls: list[str]) -> list[dict[str, object]]:
    limiter = asyncio.Semaphore(20)
    timeout = aiohttp.ClientTimeout(total=30, connect=5)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks: list[asyncio.Task[dict[str, object]]] = []
        async with asyncio.timeout(60), asyncio.TaskGroup() as task_group:
            for url in urls:
                tasks.append(task_group.create_task(fetch_data(session, limiter, url)))

    return [task.result() for task in tasks]
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

# Protect shared mutable state explicitly
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

For connection ownership, retries, `Retry-After`, idempotency, and request budgets, use the [HTTP client resilience reference](file:///Users/Devesh_Padmanabhan/.cursor/agent-engineering-handbook/skills/python-development/references/http-client-resilience.md).

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
