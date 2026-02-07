# Troubleshooting & Debugging

## Debugging Tools

**Python Debugger (pdb):**

```python
import pdb

def complex_function(data: list[dict]) -> dict:
    """Debug with pdb breakpoint."""
    pdb.set_trace()  # Breakpoint - execution pauses here
    result = process_data(data)
    return result

# Or use breakpoint() built-in (Python 3.7+)
def complex_function(data: list[dict]) -> dict:
    breakpoint()  # Modern way - equivalent to pdb.set_trace()
    result = process_data(data)
    return result
```

**pdb Commands:**

- `n` (next): Execute next line
- `s` (step): Step into function calls
- `c` (continue): Continue execution
- `l` (list): Show current code context
- `p <variable>`: Print variable value
- `pp <variable>`: Pretty-print variable
- `u` (up): Move up stack frame
- `d` (down): Move down stack frame
- `q` (quit): Quit debugger

**IPython Debugger (ipdb):**

```python
import ipdb

def debug_function():
    ipdb.set_trace()  # Enhanced pdb with IPython features
    # Better tab completion, syntax highlighting
```

**VS Code / PyCharm Debugging:**

- Set breakpoints in IDE
- Use "Debug" configuration
- Inspect variables, call stack, watch expressions
- Step through code interactively

## Profiling & Performance Analysis

**cProfile:**

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

**line_profiler:**

```python
# Install: pip install line_profiler
# Run: kernprof -l -v script.py

@profile  # Decorator added by line_profiler
def slow_function():
    result = []
    for i in range(1000):
        result.append(i * 2)  # Line-by-line timing
    return result
```

**memory_profiler:**

```python
# Install: pip install memory_profiler
# Run: python -m memory_profiler script.py

from memory_profiler import profile

@profile
def memory_intensive():
    data = [i for i in range(1000000)]  # Memory usage per line
    return sum(data)
```

## Logging for Debugging

**Structured Debug Logging:**

```python
import logging
import sys

# Configure debug logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def debug_function(data: dict):
    logger.debug(f"Function called with data: {data}")
    logger.debug(f"Data keys: {list(data.keys())}")

    try:
        result = process(data)
        logger.debug(f"Result: {result}")
        return result
    except Exception as e:
        logger.exception("Error in debug_function", exc_info=True)
        raise
```

## Common Issues & Solutions

**Import Errors:**

```python
# BAD: Circular import
# module_a.py imports module_b.py
# module_b.py imports module_a.py

# GOOD: Restructure to avoid circular imports
# - Move shared code to separate module
# - Use late imports (inside functions)
# - Use dependency injection

# Late import pattern
def process_data():
    from module_b import helper_function  # Import inside function
    return helper_function()
```

**Memory Leaks:**

```python
# BAD: Keeping references to large objects
cache = {}
def process_large_data(data):
    cache["data"] = data  # Keeps data in memory forever

# GOOD: Use weak references or clear cache
from weakref import WeakValueDictionary

cache = WeakValueDictionary()  # Allows garbage collection

# Or use size limits
from collections import OrderedDict

class LRUCache:
    def __init__(self, max_size: int = 100):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size

    def get(self, key: str):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: any):
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest
        self.cache[key] = value
```

**String Concatenation Performance:**

```python
# BAD: Inefficient string concatenation
result = ""
for item in items:
    result += item

# GOOD: Use join or list comprehension
result = "".join(items)

# Or for complex cases:
parts = [f"{key}={value}" for key, value in data.items()]
result = "&".join(parts)
```

**Repeated Lookups:**

```python
# BAD: Repeated lookups
for key in keys:
    if key in large_dict:
        process(large_dict[key])

# GOOD: Single pass
for key in keys:
    value = large_dict.get(key)  # O(1) lookup
    if value is not None:
        process(value)
```

**Exception Debugging:**

```python
import traceback
import sys

def debug_exception():
    try:
        risky_operation()
    except Exception as e:
        # Print full traceback
        traceback.print_exc()

        # Get traceback as string
        tb_str = traceback.format_exc()
        logger.error(f"Exception occurred: {tb_str}")

        # Get exception info tuple
        exc_type, exc_value, exc_tb = sys.exc_info()
        logger.error(f"Type: {exc_type}, Value: {exc_value}")

        raise  # Re-raise to preserve stack trace
```

## Testing for Race Conditions

**Thread Safety Testing:**

```python
import threading
import time
from queue import Queue

def test_thread_safety(func, num_threads: int = 10, iterations: int = 1000):
    """Test function for thread safety."""
    results: Queue[dict] = Queue()
    errors: Queue[Exception] = Queue()

    def worker():
        try:
            for _ in range(iterations):
                result = func()
                results.put(result)
        except Exception as e:
            errors.put(e)

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    # Check for errors
    error_list = []
    while not errors.empty():
        error_list.append(errors.get())

    return {
        "results_count": results.qsize(),
        "errors": error_list,
        "elapsed_time": elapsed,
        "thread_safe": len(error_list) == 0
    }
```
