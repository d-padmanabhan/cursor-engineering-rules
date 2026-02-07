# Package Management (uv)

## Why uv?

**Prefer `uv` for new projects** - Fast, modern Python package installer and resolver.

**Installation:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Benefits:** 10-100x faster, deterministic resolution, drop-in pip replacement.

## Project Setup

```bash
# Initialize new project
uv init my-project
cd my-project

# Add dependencies
uv add boto3 pydantic

# Add dev dependencies
uv add --dev pytest black ruff mypy

# Sync dependencies (install from lock file)
uv sync

# Run script
uv run python main.py
```

## Import Sorting (isort)

**Use `isort` to automatically sort imports** - Ensures consistent import ordering across projects.

**Installation:**

```bash
uv add --dev isort
# or
pip install isort
```

**Configuration (pyproject.toml):**

```toml
[tool.isort]
profile = "black"  # Compatible with black formatting
line_length = 120
multi_line_output = 3  # Vertical hanging indent
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
skip_glob = ["*/migrations/*", "*/venv/*", "*/.venv/*"]

# Import sections: stdlib, third-party, local
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
known_first_party = ["my_package"]
```

**Usage:**

```bash
# Check import order
isort --check-only .

# Auto-fix import order
isort .

# Check specific file
isort --check-only src/main.py

# Auto-fix specific file
isort src/main.py
```

**Import order example:**

```python
# Standard library
import logging
import os
from datetime import datetime, timezone
from typing import Any

# Third-party
import boto3
import requests
from pydantic import BaseModel

# Local
from utils import setup_logger
from models import User
```

**Integration with pre-commit:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

## Creating Installable Packages

**With uv:**

```bash
# Initialize new project
uv init my-package

# Add dependencies
uv add requests pydantic

# Add dev dependencies
uv add --dev pytest black ruff

# Sync dependencies (install from lock file)
uv sync

# Run script with uv
uv run python main.py

# Build distribution
uv build

# Publish to PyPI
uv publish
```

**Development mode (editable install):**

```bash
# Development mode (editable install)
uv pip install -e .

# Production install
uv pip install .

# With optional dependencies
uv pip install ".[dev,test]"
```
