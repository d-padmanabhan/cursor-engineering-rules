---
name: python-development
description: Python development standards for code review and generation. Covers Python 3.14+ patterns including template strings (t-strings), deferred annotations, free-threading, type hints, async/await, testing with pytest, package management with uv, AWS Lambda/boto3 patterns, and Pydantic validation. Use when working with .py files, pyproject.toml, requirements.txt, Lambda functions, or when asking about Python best practices, code review, or generation.
---

# Python Development

Mandatory gates are owned by the Python rule (`${HANDBOOK_ROOT}/rules/200-python.mdc`). This skill and its references own procedures and examples.

## Guiding Principle

Apply features only when they add clarity, correctness, performance, or security. Prefer simple, intentional solutions (DRY, KISS, YAGNI, Fail Fast).

## The Zen of Python (`import this`)

The canonical aphorisms by Tim Peters (PEP 20). When in doubt about which Python idiom to choose, re-read these. Quote verbatim; do not paraphrase in code reviews.

```text
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

> Run `python -c "import this"` in any Python REPL to see it.

For per-line operative readings (how to apply each in review), see the Zen section in `rules/200-python.mdc`.

## AI Assistant Guidelines

- **Avoid Over-Engineering**: Don't recommend boto3 client caching, async/await, or concurrency patterns unless explicitly requested or bottlenecks are evident
- **Keep It Simple**: Prefer stdlib over complex architectures
- **Respect Context**: Don't transform a 20-line script into a 200-line framework

Do not review Python by asking whether every language feature or library could be inserted. Recommend a comprehension, generator, decorator, dataclass, protocol, cache, concurrency model, framework, or design pattern only when it removes concrete duplication, enforces a requirement, or addresses measured cost. State the problem first and prefer deletion or a direct implementation.

Before adding a dependency, identify the capability missing from the standard library or existing dependencies, its operational and security cost, and the smallest alternative. Assertions are for internal invariants and may be disabled; never use them to validate untrusted input or enforce authorization.

## Non-negotiables

> [!IMPORTANT]
> New Python applications, services, scheduled jobs, CLI tools, and AWS Lambda functions target **Python ≥ 3.14**. Treat lower runtimes as a reject-in-review issue unless the code is a library / SDK with a stated compatibility commitment.

### NN-1: Python ≥ 3.14 for new applications, services, and Lambda functions

Use `requires-python = ">=3.14"` in `pyproject.toml`, Python 3.14 in CI, Python 3.14 Docker images, and Python 3.14 Lambda runtimes for new code.

`requires-python` declares compatibility; it does not select one exact interpreter. For deterministic project execution, commit a `.python-version` created with an exact tested patch, for example `uv python pin 3.14.7`, and update that pin deliberately. For one-off execution, request the tested patch explicitly with `uv run --python 3.14.7 script.py`. Do not encode one patch version as an evergreen handbook constant.

Select the latest supported stable Python patch available on the deployment target, then pin and test it. Use the dependency and toolchain currency workflow (`${HANDBOOK_ROOT}/skills/core-engineering/references/dependency-and-toolchain-currency.md`) for uv lock updates, compatibility checks, and exceptions.

Libraries published to PyPI or shipped to external customers MAY target a lower floor when there is a documented compatibility commitment. The acceptable lower floor is Python 3.11. The PR description must explain the audience, the 3.14 features being deferred, and the planned floor-bump date.

Reject in review:

- New application / service / Lambda with `requires-python = ">=3.11"` (or lower) and no library-audience justification
- Missing `requires-python` in `pyproject.toml`
- New code targeting Python 3.10 or below for any reason
- CI, Docker, or Lambda runtime config pinned below Python 3.14 for new app / service / Lambda code

### NN-2: Leading underscores mean non-public API

Do not prefix functions, methods, classes, variables, modules, or packages with `_` unless they are intentionally internal implementation details. Public behavior gets public names.

```python
# Public API, public name
def validate_order(order: Order) -> None:
    ...


# Internal helper, module-private name
def _normalize_order_id(raw_order_id: str) -> str:
    ...
```

Reject in review:

- `_process_data()`, `_validate_input()`, or `_build_payload()` called directly from other modules
- Public classes / modules named `_Client`, `_Service`, `_helpers`, or similar
- Double-underscore methods (`__method`) unless name-mangling is intentionally required
- Invented dunder names such as `__process__` or `__validate__`
- Leading underscore added merely because the function is small or "helper-ish"

## Standards Quick Reference

| Aspect | Standard |
|--------|----------|
| **Python Version** | ≥ 3.14 |
| **Executable PEP 723 script shebang** | `#!/usr/bin/env -S uv run --script` |
| **Formatting** | 4-space indents, 120 char line length |
| **Linting** | Repository-configured formatter, Ruff, type checker, and Pylint score ≥9.0 when Pylint is configured |
| **Type Hints** | Strict typing required |
| **Docstrings** | Google-style |
| **Package Manager** | `uv` for new projects and standalone scripts |

## Documentation Contract

Only executable standalone scripts need a shebang. For a PEP 723 script, place inline metadata immediately after `#!/usr/bin/env -S uv run --script`; the `dependencies` field is required even when empty. Put the module docstring after the metadata. Import-only modules, tests, package files, and AWS Lambda handlers do not need a uv shebang.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Process user export files and publish normalized records.

This script reads a JSON export, validates each record, writes a cleaned
CSV file, and optionally uploads the result to object storage.

Workflow:
1. Parse command-line arguments.
2. Validate input file and output directory.
3. Load and validate JSON records.
4. Write normalized CSV output.
5. Upload the result when --upload is set.

Usage:
    python process_users.py --input users.json --output users.csv
    python process_users.py --input users.json --output users.csv --upload
"""
```

Every public function, class, and method must use Google-style docstrings. Start with a concise summary immediately after the opening triple quotes, then document arguments, return values, raised exceptions, and examples when helpful.

```python
def load_users(input_path: Path) -> list[User]:
    """Load user records from a JSON file.

    Args:
        input_path: Path to the JSON file containing user records.

    Returns:
        Validated user records parsed from the input file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the file contains invalid JSON or invalid user records.

    Example:
        users = load_users(Path("users.json"))
    """
```

Inline comments are for complex logic, non-obvious tradeoffs, or external constraints. Do not comment obvious assignments or restate function names.

## Type Hints

Use built-in types instead of `typing` module:

```python
# Modern Python 3.14+
def process(items: list[str], config: dict[str, int] | None = None) -> tuple[str, int]:
    ...

# Avoid (old style)
from typing import List, Dict, Optional, Tuple
def process(items: List[str], config: Optional[Dict[str, int]] = None) -> Tuple[str, int]:
    ...
```

Annotate function parameters, return values, public attributes, empty collections, and local variables whose inferred type is unclear or intentionally wider than the initializer. Do not annotate every obvious local assignment; redundant annotations add noise without improving static analysis.

## Diagnostic Suppression Policy

Pylint, Ruff, and type-checker scores are quality signals, not objectives to game. Never add `# pylint: disable`, `# noqa`, `# type: ignore`, coverage exclusions, or configuration-level ignores solely to increase a score or make CI green.

Fix the code, types, stubs, or narrowly incorrect configuration first. When a real tool limitation or third-party defect leaves no clearer solution:

- scope the suppression to one statement or one symbolic diagnostic code;
- prohibit bare `# type: ignore`, bare `# noqa`, `disable=all`, category-wide, file-wide, and project-wide suppression;
- document the technical reason and why a code-level fix is unsafe or impossible;
- link temporary suppressions to an owner, issue, expiry date, and removal trigger;
- prefer `Protocol`, `TypeGuard`, `cast`, corrected stubs, or targeted tool configuration when those express the truth;
- review existing suppressions as debt and remove them when the limitation is resolved.

A 10/10 Pylint score obtained by hiding findings is a failure. Meet the repository floor with the intended checks enabled and no unjustified suppression.

## Imports, Strings, and Naming

- Group imports as standard library, third-party, and local, with one blank line between groups.
- Sort imports alphabetically using Ruff's `I` rules or isort rather than maintaining order manually.
- Use double quotes by default. Configure Ruff or Black to preserve the convention and allow single quotes when they avoid escaping embedded double quotes.
- Use precise domain names. A leading underscore is reserved for intentionally non-public APIs.

## Python 3.14 Features (Released Oct 2025)

### Template String Literals (PEP 750)

T-strings preserve static text and interpolations for a processor to inspect. They do not parameterize SQL or escape HTML on their own; safety depends on the processor.

```python
message_template = t"Processed order {order_id} for {customer_name}"
message = render_audit_message(message_template)
```

### Deferred Annotation Evaluation (PEP 649)

Annotations are no longer evaluated eagerly, improving startup performance:

```python
# Annotations stored in __annotate__ function
# Evaluated only when inspect.get_annotations() is called
def process(data: ComplexType) -> Result:
    """Annotations evaluated lazily, not at import time."""
    ...
```

### Free-Threading Support (PEP 779)

Free-threaded CPython builds can run threads in parallel without the GIL. They are optional, can use more memory, and may re-enable the GIL when an extension is not compatible. Benchmark the real dependency set before selecting this runtime.

```python
# Enable with: python3.14t (free-threaded build)
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(cpu_intensive_task, items)
```

### UUID6, UUID7, and UUID8 Support

Modern UUID versions with better properties:

```python
import uuid

# UUID7: time-ordered and useful when index locality matters
event_id = uuid.uuid7()

# UUID8: application-defined integer blocks, not cryptographically secure
custom_id = uuid.uuid8(0x12345678, 0x9ABCDEF0, 0x11223344)

# Use UUID4 for a security-sensitive random identifier
security_token_id = uuid.uuid4()
```

## Code Structure

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Module purpose and overview.

Workflow:
1. Load configuration
2. Validate inputs
3. Process data
"""

# Standard library
import logging
import sys

# Third-party
import requests

# Local
from utils import helper


def load_configuration() -> Config:
    """Load the application configuration."""
    pass


def main() -> int:
    """Run the application."""
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Order functions by call hierarchy so readers encounter dependencies before callers when practical. Keep the entry point last.

## Key Patterns

### Defensive Programming

```python
# Validate inputs early (fail-fast)
def process_user(user_id: str | None) -> User:
    if user_id is None:
        raise ValueError("user_id is required")
    # Continue processing...
```

### No Mutable Defaults

```python
# BAD
def foo(items: list[str] = []):
    ...

# GOOD
def foo(items: list[str] | None = None):
    if items is None:
        items = []
    ...
```

### Error Handling

```python
# Catch the specific failure that this boundary can translate.
try:
    data = load_database()
except DatabaseConnectionError as error:
    raise RuntimeError("Failed to load database") from error
```

Catch `Exception` only at an intentional process, task, or request boundary that must record failure before terminating or returning a safe response. Log with traceback context and re-raise or translate; never continue as though the operation succeeded.

### Logging Setup

```python
import logging
import time

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    class UTCFormatter(logging.Formatter):
        converter = time.gmtime
    
    handler = logging.StreamHandler()
    handler.setFormatter(UTCFormatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger

logger = setup_logger(__name__)
```

## Package Management (uv)

Use `pyproject.toml` and `uv.lock` for new projects. Do not introduce `requirements.txt` into a new uv-managed project, but do not migrate an existing supported requirements workflow unless the task includes that migration.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Project setup
uv init my-project
cd my-project
uv python pin 3.14.7
uv add boto3 pydantic
uv add --dev pytest black ruff
uv sync

# Run script
uv run python main.py
```

## Pydantic Validation

Use Pydantic at structured trust boundaries when runtime validation, explicit coercion, or schema generation adds value. Do not add it for already trusted internal data that a dataclass or typed domain object represents clearly. Follow the Pydantic validation reference (`${HANDBOOK_ROOT}/skills/python-development/references/pydantic-validation.md`).

## Quick Checklist

- [ ] `uv run --script` shebang and complete PEP 723 metadata for executable standalone scripts
- [ ] Exact tested Python patch pinned for deterministic project execution
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] Imports grouped and alphabetically sorted
- [ ] Double-quote convention enforced by formatter
- [ ] `if __name__ == "__main__":` guard
- [ ] Logging configured
- [ ] Input validation
- [ ] Specific exception handling
- [ ] `black` and `ruff` pass
- [ ] `pylint` score ≥ 9.0
- [ ] No unjustified or score-driven diagnostic suppressions

## Detailed References

- **Code Quality Tools**: See code quality tools (`${HANDBOOK_ROOT}/skills/python-development/references/code-quality-tools.md`) for Black, Ruff, mypy, and Pylint configuration
- **Package Management**: See package management (`${HANDBOOK_ROOT}/skills/python-development/references/package-management.md`) for uv and dependency management
- **Standard Library**: See standard library (`${HANDBOOK_ROOT}/skills/python-development/references/standard-library.md`)
- **Observability**: Use the observability skill (`${HANDBOOK_ROOT}/skills/observability/SKILL.md`) for schemas, metrics, tracing, SLOs, alerts, and pipelines; see Python logging (`${HANDBOOK_ROOT}/skills/python-development/references/logging-observability.md`) for runtime-specific implementation
- **Security & Validation**: See security and validation (`${HANDBOOK_ROOT}/skills/python-development/references/security-validation.md`)
- **Error Handling**: See error handling (`${HANDBOOK_ROOT}/skills/python-development/references/error-handling.md`)
- **Performance Optimization**: See performance optimization (`${HANDBOOK_ROOT}/skills/python-development/references/performance-optimization.md`)
- **Troubleshooting & Debugging**: See troubleshooting and debugging (`${HANDBOOK_ROOT}/skills/python-development/references/troubleshooting-debugging.md`)
- **Design Patterns**: See design patterns (`${HANDBOOK_ROOT}/skills/python-development/references/design-patterns.md`)
- **CLI & User Experience**: See CLI and user experience (`${HANDBOOK_ROOT}/skills/python-development/references/cli-user-experience.md`)
- **Modern Python Features**: See modern Python (`${HANDBOOK_ROOT}/skills/python-development/references/modern-python.md`)
- **Async & Concurrency**: See async and concurrency (`${HANDBOOK_ROOT}/skills/python-development/references/async-concurrency.md`)
- **HTTP Clients**: See HTTP client resilience (`${HANDBOOK_ROOT}/skills/python-development/references/http-client-resilience.md`)
- **Pagination & Streaming**: See pagination and streaming (`${HANDBOOK_ROOT}/skills/python-development/references/pagination-streaming.md`)
- **Pydantic**: See Pydantic validation (`${HANDBOOK_ROOT}/skills/python-development/references/pydantic-validation.md`)
- **Testing Patterns**: See testing patterns (`${HANDBOOK_ROOT}/skills/python-development/references/testing-patterns.md`)
- **AWS Lambda**: See AWS Lambda (`${HANDBOOK_ROOT}/skills/python-development/references/aws-lambda.md`)
- **AWS and Boto3**: See AWS and Boto3 (`${HANDBOOK_ROOT}/skills/python-development/references/aws-boto3.md`)
