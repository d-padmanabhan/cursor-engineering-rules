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
    raise FileNotFoundError(
        f"File not found: {file}\n"
        f"Current directory: {Path.cwd()}\n"
        f"Available files: {list(Path.cwd().glob('*.txt'))}"
    )
```

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
def process_files(files: list[str], dry_run: bool = False) -> None:
    """Process files with dry-run support."""
    for file in files:
        if dry_run:
            print(f"[DRY RUN] Would process: {file}")
            print(f"[DRY RUN] Would execute: process_file('{file}')")
        else:
            process_file(file)
            print(f"Processed: {file}")
```
