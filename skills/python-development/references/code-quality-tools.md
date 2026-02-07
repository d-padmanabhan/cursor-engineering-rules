# Code Quality Tools & Configuration

## Formatting & Linting Commands

**Complete workflow:**

```bash
# Format with black
black . --line-length=120

# Sort imports with isort
isort . --profile=black --line-length=120

# Run both together
black . && isort .

# Check without modifying files
black --check . && isort --check-only .

# Run both checks
black --check . && isort --check-only .

# Run ruff for linting
ruff check .

# Auto-fix issues
ruff check --fix .

# Check specific file
ruff check src/main.py

# Strict type checking (recommended)
mypy --strict .

# Type check specific file
mypy --strict src/main.py

# Alternative: Use ty (faster, recommended)
ty check .

# Run pylint on file/directory
pylint src/main.py

# Run with specific score threshold (fail if below 9.5)
pylint --fail-under=9.5 src/

# Run on entire project
pylint --fail-under=9.5 .

# Generate report
pylint --output-format=json src/ > pylint-report.json
```

## Complete Quality Check Workflow

```bash
# Full quality check (modifies files)
black . && isort . && ruff check --fix . && mypy --strict .

# OR (faster)
ruff check --fix . && mypy --strict .

# Check-only mode (CI/pre-commit)
black --check . && \
isort --check-only . && \
ruff check . && \
mypy --strict . && \
pylint --fail-under=9.5 . && \
bandit -r . -ll
```

## Configuration Files

**pyproject.toml (Recommended):**

```toml
[tool.black]
line-length = 120
target-version = ['py314']

[tool.isort]
profile = "black"
line_length = 120

[tool.ruff]
line-length = 120
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.mypy]
python_version = "3.14"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pylint.messages_control]
disable = ["C0103", "C0111"]  # Disable specific checks if needed

[tool.pylint.format]
max-line-length = 120
```

**pylintrc (Optional, for project-specific config):**

```ini
[FORMAT]
max-line-length=120

[MESSAGES CONTROL]
disable=
    C0103,  # invalid-name (if using non-standard naming)
    C0111,  # missing-docstring (if docstrings not required)

[REPORTS]
output-format=text
score=yes
```

## Pylint Score Targets

**Score interpretation:**

- **10.0** - Perfect (rare, may require disabling some checks)
- **9.5-9.9** - Excellent (target for production code)
- **9.0-9.4** - Good (acceptable, but aim higher)
- **<9.0** - Needs improvement

**Common issues that lower score:**

- Missing docstrings
- Long lines (>120 chars)
- Too many arguments (>5)
- Too many local variables (>15)
- Cyclomatic complexity (>10)

**Improving pylint score:**

```bash
# Run pylint to see issues
pylint path/to/file.py

# Fix issues incrementally:
# 1. Add missing docstrings
# 2. Break up complex functions
# 3. Reduce function arguments
# 4. Fix naming conventions
# 5. Add type hints
```

## Pre-commit Integration

**Add to `.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=120]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--strict]
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pylint
        name: pylint
        entry: pylint
        language: system
        args: [--fail-under=9.5]
        types: [python]
```

## CI/CD Integration

**GitHub Actions example:**

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install dependencies
        run: |
          uv sync

      - name: Format check
        run: |
          black --check .
          isort --check-only .

      - name: Lint
        run: |
          ruff check .

      - name: Type check
        run: |
          mypy --strict .

      - name: Pylint
        run: |
          pylint --fail-under=9.5 .
```

## Security Scanning

**Bandit:**

```bash
# Install
uv add --dev bandit
# or
pip install bandit

# Scan codebase
bandit -r .                    # Recursive scan
bandit -r . -f json -o report.json  # JSON output
bandit -r . -ll                # Low severity and above
bandit -r . -ii                # Medium confidence and above

# Exclude paths
bandit -r . -x tests/,venv/

# Use config file (.bandit)
bandit -r . -c .bandit
```
