---
name: bash-shell-scripting
description: Bash scripting best practices for production-grade scripts, CLI tools, and Makefiles. Covers strict mode, error handling, portability, performance patterns, and argument parsing. Use when working with .sh files, Makefiles, shell scripts, or when asking about Bash, shell scripting, CLI design, or command-line tools.
---

# Bash & Shell Scripting

## Core Principles

- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple
- **Fail Fast**: Exit on errors immediately
- **Zero Warnings**: Must pass shellcheck

## Quick Reference

```bash
set -euo pipefail           # Strict mode (fail-fast)
set -uo pipefail            # Controlled mode (explicit error handling)
set -Euo pipefail           # Strict + ERR trap propagation
command -v cmd >/dev/null   # Check if command exists (portable)
trap 'cleanup' EXIT         # Always cleanup
flock -n 200 || exit 1      # Prevent concurrent runs
readonly VAR="value"        # Immutable constant
local var="value"           # Function-local variable
```

## Core Standards

| Aspect | Standard |
|--------|----------|
| **Shebang** | `#!/usr/bin/env bash` or `#!/bin/bash` |
| **Safety Mode** | `set -euo pipefail` (strict) or `set -uo pipefail` (controlled) |
| **Linting** | Must pass `shellcheck` with 0 errors/warnings |
| **Formatting** | Must pass `shfmt -i 2 -ci -sr -bn` |
| **Extension** | `.sh` for scripts |

## Error Handling Modes

### Strict Mode (Fail-Fast)

```bash
set -euo pipefail  # Exit immediately on any error
```

Use for: Simple linear scripts, dependency installation, straightforward validation.

### Controlled Mode (Explicit)

```bash
set -uo pipefail  # No -e: handle errors explicitly
```

Use for: Diagnostics, cleanup operations, commands where failure is expected.

### Strict + ERR Trap

```bash
set -Euo pipefail

trap 'echo "ERROR in ${FUNCNAME[0]:-main} at line $LINENO"' ERR
```

Use for: Production scripts with comprehensive error handling.

## Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"

cleanup() {
    rm -f "${TEMP_FILE:-}" 2>/dev/null || true
}
trap cleanup EXIT

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >&2
}

die() {
    log "ERROR: $*"
    exit 1
}

main() {
    local arg="${1:-}"
    [[ -z "$arg" ]] && die "Usage: $SCRIPT_NAME <argument>"
    
    log "Processing: $arg"
    # Main logic here
}

main "$@"
```

## Best Practices

### Always Quote Variables

```bash
# ✅ GOOD
echo "${var}"
[[ -n "${var:-}" ]] && echo "set"

# ❌ BAD
echo $var
[ -n $var ] && echo "set"
```

### Use Functions

```bash
process_file() {
    local file="$1"
    [[ -f "$file" ]] || return 1
    # Process file
}
```

### Check Command Existence

```bash
command -v docker >/dev/null 2>&1 || die "docker is required"
```

### Temporary Files

```bash
readonly TEMP_FILE="$(mktemp)"
trap 'rm -f "$TEMP_FILE"' EXIT

echo "data" > "$TEMP_FILE"
```

### Lock Files

```bash
exec 200>"/tmp/${SCRIPT_NAME}.lock"
flock -n 200 || { echo "Already running"; exit 1; }
```

## Performance Patterns

### Avoid Subshells in Loops

```bash
# ❌ BAD - subshell, variables don't persist
count=0
cat file.txt | while read -r line; do
    count=$((count + 1))
done
echo "$count"  # Empty! (subshell issue)

# ✅ GOOD - process substitution
count=0
while read -r line; do
    count=$((count + 1))
done < file.txt
echo "$count"  # Correct
```

### Use Arrays

```bash
# Arrays for multiple values
files=("file1.txt" "file2.txt" "file3.txt")
for file in "${files[@]}"; do
    process "$file"
done

# Append to array
files+=("file4.txt")
```

## Argument Parsing

```bash
show_help() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] <file>

Options:
    -h, --help      Show this help
    -v, --verbose   Enable verbose mode
    -o, --output    Output file (default: stdout)
EOF
}

parse_args() {
    VERBOSE=false
    OUTPUT=""
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help) show_help; exit 0 ;;
            -v|--verbose) VERBOSE=true; shift ;;
            -o|--output) OUTPUT="$2"; shift 2 ;;
            -*) die "Unknown option: $1" ;;
            *) break ;;
        esac
    done
    
    [[ $# -eq 0 ]] && die "Missing required argument"
    INPUT_FILE="$1"
}
```

## Detailed References

- **Shell Utilities**: See [references/shell-utilities.md](references/shell-utilities.md) for curl, jq, lynx
- **Makefile Patterns**: See [references/makefile-patterns.md](references/makefile-patterns.md)
- **CLI Design**: See [references/cli-design.md](references/cli-design.md)
- **Justfile Patterns**: See [references/justfile.md](references/justfile.md)
- **Repo Sync (rsync)**: See [references/rsync-repo-sync.md](references/rsync-repo-sync.md)
