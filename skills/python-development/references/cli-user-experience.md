# CLI & User Experience

## argparse

**argparse:** Add CLI options:

```python
import argparse

parser = argparse.ArgumentParser(
    description="Process user data",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output")
parser.add_argument("--config", type=str, default="config.yaml", help="Config file path")
parser.add_argument("files", nargs="+", help="Files to process")

args = parser.parse_args()

if args.dry_run:
    print("Dry run mode - no changes will be made")

if args.verbose >= 2:
    logging.getLogger().setLevel(logging.DEBUG)
elif args.verbose >= 1:
    logging.getLogger().setLevel(logging.INFO)
```

## typer

**typer:** Modern CLI framework (alternative to argparse).

```python
import typer

app = typer.Typer()

@app.command()
def process(
    file: str = typer.Argument(..., help="File to process"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Preview without executing"),
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Verbose output"),
):
    """Process a file."""
    if dry_run:
        typer.echo(f"Would process: {file}")
        return
    
    typer.echo(f"Processing: {file}")
    # Process file...

if __name__ == "__main__":
    app()
```

## rich

**rich:** Rich text and progress bars:

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

console = Console()

# Progress bars
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console,
) as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        time.sleep(0.01)
        progress.update(task, advance=1)

# Tables
table = Table(title="Users")
table.add_column("ID", style="cyan")
table.add_column("Name", style="magenta")
table.add_column("Email", style="green")

table.add_row("1", "Alice", "alice@acme.com")
table.add_row("2", "Bob", "bob@acme.com")
console.print(table)

# Panels
console.print(Panel("Important message", title="Notice", border_style="yellow"))
```

## User Experience Best Practices

**Clear Error Messages:**

```python
# BAD: Cryptic error
if not file.exists():
    raise ValueError("Error")

# GOOD: Clear error message
if not file.exists():
    raise FileNotFoundError(f"Input file not found: {file}")
```

Do not enumerate directory contents or expose unrestricted environment details in user-facing errors.

**Progress Indicators:**

```python
from tqdm import tqdm

# Progress bar for loops
for item in tqdm(items, desc="Processing"):
    process(item)

# Manual progress updates
with tqdm(total=100) as pbar:
    for i in range(100):
        process_item(i)
        pbar.update(1)
```

**Dry-Run Mode:**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedAction:
    """Describe one externally visible action."""

    action: str
    target: str


def build_plan(files: list[str]) -> list[PlannedAction]:
    """Build the same deterministic plan used by preview and execution."""
    return [PlannedAction(action="process", target=file) for file in files]


def run_plan(actions: list[PlannedAction], *, dry_run: bool) -> None:
    """Preview or execute a complete action plan."""
    for action in actions:
        if dry_run:
            print(f"[DRY RUN] Would {action.action}: {action.target}")
            continue
        execute_action(action)
```

A dry run must suppress every externally visible side effect: file/database writes, API mutations, messages, notifications, subprocess mutations, and infrastructure changes. Preview the exact normalized targets and action types without exposing secrets. For destructive execution, show the plan at the human confirmation gate and reject stale approval if the plan changes.
