# Justfile patterns

`just` is a command runner that makes common dev tasks reproducible and discoverable.

## When to use

- Replace fragile copy/paste command docs
- Provide a single entry point for lint/test/build/deploy commands
- Reduce “works on my machine” drift with consistent flags

---

## Naming and structure

- Use short, verb-based recipe names: `fmt`, `lint`, `test`, `build`, `plan`
- Keep recipes idempotent where possible
- Prefer explicit dependencies between recipes

---

## Safe defaults

### Avoid accidental destructive operations

- Provide a `plan` before `apply`
- Prefer explicit confirmation prompts for destructive tasks

### Prefer non-interactive outputs in CI

- Use flags that make commands deterministic and CI-friendly

---

## Example justfile

```makefile
set shell := ["bash", "-euo", "pipefail", "-c"]

default:
  @just --list

fmt:
  @echo "Formatting..."
  @pre-commit run --all-files

lint:
  @echo "Linting..."
  @pre-commit run --all-files

test:
  @echo "Running tests..."
  @pytest -q

plan:
  @terraform fmt -recursive
  @terraform validate
  @terraform plan
```

> [!TIP]
> Keep heavy “environment setup” out of `just`. Document prerequisites in README or a `bootstrap` recipe.
