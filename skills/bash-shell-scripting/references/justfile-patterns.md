# Justfile Patterns

Standardized justfile patterns for consistent project commands across platforms and languages.

## Why Just over Make?

| Feature | Make | Just |
|---------|------|------|
| Cross-platform | Requires GNU Make | Works consistently everywhere |
| PHONY declarations | Required for non-file targets | Not needed (all recipes are "phony") |
| Default recipe | Requires explicit `default:` | First recipe or `default` |
| Help/listing | Manual implementation | Built-in `just --list` |
| Variables | Complex syntax `$(VAR)` | Simple syntax `{{var}}` |
| Parameters | Awkward | Native support |
| String interpolation | Limited | Full support |
| Error messages | Cryptic | Clear and helpful |

## Installation

```bash
# macOS
brew install just

# Cargo (cross-platform)
cargo install just

# Other platforms: https://github.com/casey/just#installation
```

## Core Principles

- **Consistency**: Common interface across all components regardless of technology
- **Simplicity**: Hide platform-specific commands behind standard recipes
- **Discoverability**: `just --list` shows all available commands with descriptions
- **Platform Independence**: Works across different languages and toolchains

## Standard Template

```just
# Show available recipes
default:
    @just --list

# Set up and validate the local development environment
init:
    ./scripts/init.sh

# Install all dependencies
install:
    npm install  # or pip install -r requirements.txt, etc.

# Run in development mode (with live reload)
dev:
    npm run dev  # or python -m flask run, etc.

# Validate code formatting and linting
lint:
    npm run lint  # or ruff check, etc.

# Auto-fix linting issues
lint-fix:
    npm run lint:fix  # or ruff check --fix, etc.

# Run tests
test:
    npm test  # or pytest, etc.

# Run tests with coverage
test-coverage:
    npm test -- --coverage  # or pytest --cov, etc.

# Build the project for distribution
build:
    npm run build  # or go build, etc.

# Remove build artifacts and temporary files
clean:
    rm -rf dist/ node_modules/.cache/

# Run all CI checks
ci: lint test build
    @echo "CI checks passed"
```

## Standard Recipes

| Recipe | Purpose |
|--------|---------|
| `init` | Setup and validate local development environment |
| `install` | Install all dependencies |
| `dev` | Run in development mode (live reload) |
| `lint` | Validate formatting and linting |
| `lint-fix` | Auto-fix linting issues |
| `test` | Run unit tests |
| `test-watch` | Run tests in watch mode |
| `test-coverage` | Run tests with coverage |
| `build` | Build for distribution |
| `clean` | Remove build artifacts |
| `fmt` | Format code |

> [!NOTE]
> Use hyphens (`lint-fix`) not colons (`lint:fix`) for recipe names. Colons have special meaning in just.

## Just Features

### Variables and Settings

```just
# Settings
set shell := ["bash", "-euc"]
set dotenv-load := true

# Variables
version := `git describe --tags --always 2>/dev/null || echo "dev"`
commit := `git rev-parse --short HEAD 2>/dev/null || echo "unknown"`
build_time := `date -u +"%Y-%m-%d_%H:%M:%S"`

# Build with version info
build:
    go build -ldflags "-X main.Version={{version}} -X main.Commit={{commit}}" -o bin/app .
```

### Recipe Parameters

```just
# Deploy to specific environment
deploy env="dev":
    terraform apply -var="environment={{env}}"

# Usage: just deploy prod
```

### Conditional Logic

```just
# Platform-specific commands
install-tools:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    else
        apt-get install -y jq
    fi
```

### Dependencies

```just
# Recipe with dependencies
ci: lint test build
    @echo "All CI checks passed"

# Build depends on clean
build: clean
    go build -o bin/app .
```

### Private Recipes

```just
# Private recipe (not shown in --list)
[private]
_setup:
    mkdir -p bin/

build: _setup
    go build -o bin/app .
```

### Confirmation Prompts

```just
# Require confirmation before dangerous operations
[confirm("Are you sure you want to delete all data?")]
nuke:
    rm -rf data/
```

> [!IMPORTANT]
> Treat `[confirm("...")]` as a **HITL (human-in-the-loop)** safeguard for destructive operations.

## Best Practices

### Use Shebang for Complex Logic

```just
# ✅ GOOD: Complex logic in shebang recipe
init:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "Created .env file"
    fi
    npm install

# ❌ BAD: Complex inline commands
init-bad:
    @if [ ! -f .env ]; then cp .env.example .env; fi
    npm install
```

### Hide Command Output with @

```just
# Show only command output, not the command itself
test:
    @pytest -v

# Show command being run (default)
build:
    go build -o bin/app .
```

### Load Environment Variables

```just
# Load .env file automatically
set dotenv-load := true

deploy:
    echo "Deploying to $ENVIRONMENT"
```

### Default Values for Parameters

```just
# With default value
deploy env="dev" region="us-east-1":
    terraform apply -var="environment={{env}}" -var="region={{region}}"

# Usage:
# just deploy           -> env=dev, region=us-east-1
# just deploy prod      -> env=prod, region=us-east-1
# just deploy prod eu   -> env=prod, region=eu
```

## Examples

See [bash-shell-scripting/references/makefile-patterns.md](makefile-patterns.md) for more examples adapted to justfile syntax.

## Security Considerations

- Don't hardcode secrets in justfiles
- Use environment variables or `.env` files for sensitive values
- Use `set dotenv-load` to load `.env` files
- Validate required environment variables before running commands
- Use `[confirm]` attribute for destructive operations

## Review Checklist

- [ ] Has descriptive comments for each recipe
- [ ] Uses `set shell` for consistent behavior
- [ ] Standard recipes are present (`init`, `dev`, `lint`, `test`, `build`)
- [ ] No hardcoded secrets or credentials
- [ ] Uses parameters with defaults where appropriate
- [ ] Complex logic uses shebang recipes
- [ ] Destructive operations have `[confirm]` attribute
- [ ] Consistent with project's language/framework conventions

## Resources

- [Just Manual](https://just.systems/man/en/)
- [Just GitHub Repository](https://github.com/casey/just)
