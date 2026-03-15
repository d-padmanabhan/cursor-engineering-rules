#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Install optional Cursor hooks (deterministic lifecycle scripts).

This script can install:
  - User hooks:    ~/.cursor/hooks.json + ~/.cursor/hooks/*.py
  - Project hooks: <repo>/.cursor/hooks.json + <repo>/.cursor/hooks/*.py

By default, it MERGES into an existing hooks.json (idempotent) and creates a
timestamped backup before writing.

Usage:
  cursor-hooks-install.sh --user
  cursor-hooks-install.sh --project /path/to/repo

Options:
  -n, --dry-run         Show actions without writing files
  --user                Install into ~/.cursor
  --project <dir>       Install into <dir>/.cursor
  --no-merge            Do not modify existing hooks.json (only copy scripts)
  --force               Overwrite hooks.json with the example file (still backs up)
  -h, --help            Show help
EOF
}

die() {
  echo "ERROR: $*" 1>&2
  exit 1
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HOOKS_SRC_DIR="${REPO_ROOT}/hooks/cursor"

DRY_RUN="0"
MODE=""
TARGET_DIR=""
MERGE="1"
FORCE="0"

if [[ ! -d "${HOOKS_SRC_DIR}" ]]; then
  die "hooks source dir not found: ${HOOKS_SRC_DIR}"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--dry-run) DRY_RUN="1"; shift ;;
    --user) MODE="user"; shift ;;
    --project)
      MODE="project"
      TARGET_DIR="${2:-}"
      [[ -n "${TARGET_DIR}" ]] || die "--project requires a directory"
      shift 2
      ;;
    --no-merge) MERGE="0"; shift ;;
    --force) FORCE="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown arg: $1 (try --help)" ;;
  esac
done

[[ -n "${MODE}" ]] || die "must pass --user or --project"

if [[ "${MODE}" == "user" ]]; then
  TARGET_DIR="${HOME}/.cursor"
  HOOKS_JSON_SRC="${HOOKS_SRC_DIR}/hooks.user.example.json"
  HOOKS_JSON_DST="${TARGET_DIR}/hooks.json"
  HOOKS_DST_DIR="${TARGET_DIR}/hooks"
elif [[ "${MODE}" == "project" ]]; then
  TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"
  HOOKS_JSON_SRC="${HOOKS_SRC_DIR}/hooks.project.example.json"
  HOOKS_JSON_DST="${TARGET_DIR}/.cursor/hooks.json"
  HOOKS_DST_DIR="${TARGET_DIR}/.cursor/hooks"
else
  die "invalid mode: ${MODE}"
fi

[[ -f "${HOOKS_JSON_SRC}" ]] || die "hooks json example not found: ${HOOKS_JSON_SRC}"

log() {
  echo "==> $*"
}

run() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    printf '[dry-run]'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

install_scripts() {
  log "Installing hook scripts to: ${HOOKS_DST_DIR}"
  run mkdir -p "${HOOKS_DST_DIR}"
  run cp "${HOOKS_SRC_DIR}"/*.py "${HOOKS_DST_DIR}/"
  run chmod +x "${HOOKS_DST_DIR}/"*.py
}

backup_file() {
  local path="$1"
  [[ -f "${path}" ]] || return 0
  local ts
  ts="$(date +%Y%m%d_%H%M%S)"
  run cp "${path}" "${path}.bak.${ts}"
}

write_or_merge_hooks_json() {
  if [[ "${MERGE}" == "0" && -f "${HOOKS_JSON_DST}" ]]; then
    log "Skipping hooks.json modification (--no-merge): ${HOOKS_JSON_DST}"
    return 0
  fi

  run mkdir -p "$(dirname "${HOOKS_JSON_DST}")"
  backup_file "${HOOKS_JSON_DST}"

  if [[ "${FORCE}" == "1" || ! -f "${HOOKS_JSON_DST}" ]]; then
    log "Writing hooks.json from example: ${HOOKS_JSON_DST}"
    run cp "${HOOKS_JSON_SRC}" "${HOOKS_JSON_DST}"
    return 0
  fi

  if [[ "${MERGE}" == "1" ]]; then
    log "Merging hooks into existing hooks.json: ${HOOKS_JSON_DST}"
    if [[ "${DRY_RUN}" == "1" ]]; then
      printf '[dry-run] %q %q %q %q\n' python3 '<merge hooks json>' "${HOOKS_JSON_DST}" "${HOOKS_JSON_SRC}"
      return 0
    fi

    python3 - "${HOOKS_JSON_DST}" "${HOOKS_JSON_SRC}" <<'PY'
import json
import sys
from pathlib import Path

dst_path = Path(sys.argv[1])
src_path = Path(sys.argv[2])

def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data

dst = load(dst_path)
src = load(src_path)

if dst.get("version") != 1:
    raise SystemExit(f"Refusing to merge: {dst_path} version != 1")
if src.get("version") != 1:
    raise SystemExit(f"Invalid source: {src_path} version != 1")

dst_hooks = dst.setdefault("hooks", {})
src_hooks = src.get("hooks", {})
if not isinstance(dst_hooks, dict) or not isinstance(src_hooks, dict):
    raise SystemExit("Invalid hooks shape (expected objects)")

def norm_hook_entry(entry: dict) -> str:
    # Stable string form for dedupe
    return json.dumps(entry, sort_keys=True, separators=(",", ":"))

for hook_name, entries in src_hooks.items():
    if not isinstance(entries, list):
        continue
    existing = dst_hooks.setdefault(hook_name, [])
    if not isinstance(existing, list):
        dst_hooks[hook_name] = existing = []

    existing_norm = {norm_hook_entry(e) for e in existing if isinstance(e, dict)}
    for e in entries:
        if not isinstance(e, dict):
            continue
        if norm_hook_entry(e) not in existing_norm:
            existing.append(e)
            existing_norm.add(norm_hook_entry(e))

dst_path.write_text(json.dumps(dst, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
  fi
}

log "Source hooks: ${HOOKS_SRC_DIR}"
install_scripts
write_or_merge_hooks_json

log "Done"
log "Next: restart Cursor (it hot-reloads hooks.json, but restart is the safest)"
