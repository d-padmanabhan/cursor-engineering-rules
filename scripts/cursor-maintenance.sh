#!/usr/bin/env bash
#
# cursor-maintenance.sh - Clean Cursor cache and temporary files
#
# This script safely removes cache, logs, and temporary files from
# ~/.cursor to reclaim disk space without affecting settings or extensions.
#
# Usage:
#   ./cursor-maintenance.sh [OPTIONS]
#
# Options:
#   -n, --dry-run    Show what would be deleted without actually deleting
#   -v, --verbose    Enable verbose output
#   -a, --aggressive Include additional cleanup (terminal history, backups, stale projects)
#   -d, --days N     Age threshold for stale projects (default: 30 days)
#   -h, --help       Show this help message
#
# Safe to run weekly. Cursor should be closed for best results.
#

set -uo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

readonly CURSOR_DIR="${HOME}/.cursor"
readonly VERSION="1.0.0"

# Declare separately to avoid masking return values (SC2155)
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_NAME

# Colors for output (disabled if not a terminal)
if [[ -t 1 ]]; then
  readonly RED='\033[0;31m'
  readonly GREEN='\033[0;32m'
  readonly YELLOW='\033[0;33m'
  readonly BLUE='\033[0;34m'
  readonly NC='\033[0m' # No Color
else
  readonly RED=''
  readonly GREEN=''
  readonly YELLOW=''
  readonly BLUE=''
  readonly NC=''
fi

# Default options
DRY_RUN=false
VERBOSE=false
AGGRESSIVE=false
STALE_DAYS=30

# Counters
TOTAL_SIZE=0
ITEMS_CLEANED=0

# -----------------------------------------------------------------------------
# Logging Functions
# -----------------------------------------------------------------------------

log_info() {
  printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
  printf "${GREEN}[OK]${NC} %s\n" "$1"
}

log_warn() {
  printf "${YELLOW}[WARN]${NC} %s\n" "$1"
}

log_error() {
  printf "${RED}[ERROR]${NC} %s\n" "$1" >&2
}

log_verbose() {
  if [[ "${VERBOSE}" == true ]]; then
    printf "  ${BLUE}→${NC} %s\n" "$1"
  fi
}

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

usage() {
  cat << EOF
${SCRIPT_NAME} v${VERSION} - Cursor IDE Maintenance Script

Cleans cache, logs, and temporary files from ~/.cursor to reclaim disk space.

USAGE:
    ${SCRIPT_NAME} [OPTIONS]

OPTIONS:
    -n, --dry-run      Show what would be deleted without actually deleting
    -v, --verbose      Enable verbose output
    -a, --aggressive   Include additional cleanup (terminal history, backups, stale projects)
    -d, --days N       Age threshold for stale projects in days (default: 30)
    -h, --help         Show this help message

EXAMPLES:
    ${SCRIPT_NAME}                # Standard cleanup
    ${SCRIPT_NAME} -n             # Dry run - preview what would be deleted
    ${SCRIPT_NAME} -v             # Verbose output
    ${SCRIPT_NAME} -a             # Aggressive cleanup including backups and stale projects
    ${SCRIPT_NAME} -a -d 60       # Aggressive cleanup, projects older than 60 days
    ${SCRIPT_NAME} -n -a -v       # Dry run with aggressive + verbose

CLEANED DIRECTORIES:
    Standard:
      - cache/              General cache files
      - CachedData/         Cached extension data
      - CachedExtensionVSIXs/  Downloaded extension packages
      - Code Cache/         V8 JavaScript engine cache
      - GPUCache/           GPU shader cache
      - logs/               Application logs

    Aggressive (-a):
      - Backups/            Old file backups
      - projects/*/terminals/  Terminal session history
      - projects/*          Stale project directories (older than N days)

NOTES:
    - Close Cursor before running for best results
    - User settings, extensions, and keybindings are NOT affected
    - Safe to run weekly

EOF
}

get_dir_size() {
  local dir="$1"
  if [[ -d "${dir}" ]]; then
    du -sh "${dir}" 2> /dev/null | cut -f1
  else
    echo "0B"
  fi
}

get_dir_size_bytes() {
  local dir="$1"
  if [[ -d "${dir}" ]]; then
    du -s "${dir}" 2> /dev/null | cut -f1
  else
    echo "0"
  fi
}

format_bytes() {
  local bytes=$1
  if [[ ${bytes} -ge 1073741824 ]]; then
    printf "%.2f GB" "$(echo "scale=2; ${bytes} / 1073741824" | bc)"
  elif [[ ${bytes} -ge 1048576 ]]; then
    printf "%.2f MB" "$(echo "scale=2; ${bytes} / 1048576" | bc)"
  elif [[ ${bytes} -ge 1024 ]]; then
    printf "%.2f KB" "$(echo "scale=2; ${bytes} / 1024" | bc)"
  else
    printf "%d B" "${bytes}"
  fi
}

check_cursor_running() {
  if pgrep -x "Cursor" > /dev/null 2>&1; then
    log_warn "Cursor appears to be running"
    log_warn "For best results, close Cursor before running cleanup"
    echo ""
    read -r -p "Continue anyway? [y/N] " response
    case "${response}" in
      [yY][eE][sS] | [yY])
        return 0
        ;;
      *)
        log_info "Aborted by user"
        exit 0
        ;;
    esac
  fi
}

clean_directory() {
  local dir="$1"
  local description="$2"

  if [[ ! -d "${dir}" ]]; then
    log_verbose "Skipping ${description} (not found)"
    return 0
  fi

  local size
  local size_bytes
  size=$(get_dir_size "${dir}")
  size_bytes=$(get_dir_size_bytes "${dir}")

  if [[ "${size_bytes}" -eq 0 ]]; then
    log_verbose "Skipping ${description} (empty)"
    return 0
  fi

  if [[ "${DRY_RUN}" == true ]]; then
    log_info "[DRY RUN] Would clean ${description}: ${size}"
  else
    log_info "Cleaning ${description}: ${size}"
    if rm -rf "${dir:?}"/* 2> /dev/null; then
      log_success "Cleaned ${description}"
      ((ITEMS_CLEANED++)) || true
    else
      log_warn "Partial cleanup of ${description} (some files may be in use)"
    fi
  fi

  # Track total size in KB (du -s returns KB on macOS)
  TOTAL_SIZE=$((TOTAL_SIZE + size_bytes))
}

clean_terminal_directories() {
  local projects_dir="${CURSOR_DIR}/projects"

  if [[ ! -d "${projects_dir}" ]]; then
    log_verbose "Skipping terminal history (no projects directory)"
    return 0
  fi

  local terminal_dirs
  terminal_dirs=$(find "${projects_dir}" -type d -name "terminals" 2> /dev/null || true)

  if [[ -z "${terminal_dirs}" ]]; then
    log_verbose "Skipping terminal history (none found)"
    return 0
  fi

  local total_terminal_size=0

  while IFS= read -r terminal_dir; do
    if [[ -d "${terminal_dir}" ]]; then
      local size_bytes
      size_bytes=$(get_dir_size_bytes "${terminal_dir}")
      total_terminal_size=$((total_terminal_size + size_bytes))
    fi
  done <<< "${terminal_dirs}"

  if [[ "${total_terminal_size}" -eq 0 ]]; then
    log_verbose "Skipping terminal history (empty)"
    return 0
  fi

  local size
  size=$(format_bytes $((total_terminal_size * 1024)))

  if [[ "${DRY_RUN}" == true ]]; then
    log_info "[DRY RUN] Would clean terminal history: ${size}"
  else
    log_info "Cleaning terminal history: ${size}"
    while IFS= read -r terminal_dir; do
      if [[ -d "${terminal_dir}" ]]; then
        rm -rf "${terminal_dir:?}"/* 2> /dev/null || true
      fi
    done <<< "${terminal_dirs}"
    log_success "Cleaned terminal history"
    ((ITEMS_CLEANED++)) || true
  fi

  TOTAL_SIZE=$((TOTAL_SIZE + total_terminal_size))
}

clean_stale_projects() {
  local projects_dir="${CURSOR_DIR}/projects"
  local days="${STALE_DAYS}"

  if [[ ! -d "${projects_dir}" ]]; then
    log_verbose "Skipping stale projects (no projects directory)"
    return 0
  fi

  # Find project directories not modified in the last N days
  # Exclude hidden files like .DS_Store
  local stale_projects
  stale_projects=$(find "${projects_dir}" -mindepth 1 -maxdepth 1 -type d -mtime +"${days}" 2> /dev/null || true)

  if [[ -z "${stale_projects}" ]]; then
    log_verbose "Skipping stale projects (none older than ${days} days)"
    return 0
  fi

  local total_stale_size=0
  local stale_count=0
  local stale_list=()

  while IFS= read -r project_dir; do
    if [[ -d "${project_dir}" ]]; then
      local size_bytes
      size_bytes=$(get_dir_size_bytes "${project_dir}")
      total_stale_size=$((total_stale_size + size_bytes))
      ((stale_count++)) || true
      stale_list+=("$(basename "${project_dir}")")
    fi
  done <<< "${stale_projects}"

  if [[ "${total_stale_size}" -eq 0 ]]; then
    log_verbose "Skipping stale projects (empty)"
    return 0
  fi

  local size
  size=$(format_bytes $((total_stale_size * 1024)))

  if [[ "${DRY_RUN}" == true ]]; then
    log_info "[DRY RUN] Would remove ${stale_count} stale project(s) older than ${days} days: ${size}"
    if [[ "${VERBOSE}" == true ]]; then
      for project in "${stale_list[@]}"; do
        log_verbose "Would remove: ${project}"
      done
    fi
  else
    log_info "Removing ${stale_count} stale project(s) older than ${days} days: ${size}"
    if [[ "${VERBOSE}" == true ]]; then
      for project in "${stale_list[@]}"; do
        log_verbose "Removing: ${project}"
      done
    fi
    while IFS= read -r project_dir; do
      if [[ -d "${project_dir}" ]]; then
        rm -rf "${project_dir:?}" 2> /dev/null || true
      fi
    done <<< "${stale_projects}"
    log_success "Removed ${stale_count} stale project(s)"
    ((ITEMS_CLEANED++)) || true
  fi

  TOTAL_SIZE=$((TOTAL_SIZE + total_stale_size))
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

main() {
  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -n | --dry-run)
        DRY_RUN=true
        shift
        ;;
      -v | --verbose)
        VERBOSE=true
        shift
        ;;
      -a | --aggressive)
        AGGRESSIVE=true
        shift
        ;;
      -d | --days)
        if [[ -z "${2:-}" ]] || [[ ! "${2}" =~ ^[0-9]+$ ]]; then
          log_error "Option --days requires a numeric argument"
          exit 1
        fi
        STALE_DAYS="$2"
        shift 2
        ;;
      -h | --help)
        usage
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
  done

  # Header
  echo ""
  log_info "Cursor Maintenance Script v${VERSION}"
  echo ""

  # Check if Cursor directory exists
  if [[ ! -d "${CURSOR_DIR}" ]]; then
    log_error "Cursor directory not found: ${CURSOR_DIR}"
    exit 1
  fi

  # Show current disk usage
  local current_size
  current_size=$(get_dir_size "${CURSOR_DIR}")
  log_info "Current ~/.cursor size: ${current_size}"
  echo ""

  # Check if Cursor is running
  check_cursor_running

  # Dry run notice
  if [[ "${DRY_RUN}" == true ]]; then
    log_warn "DRY RUN MODE - No files will be deleted"
    echo ""
  fi

  # Standard cleanup directories
  log_info "Standard cleanup:"
  clean_directory "${CURSOR_DIR}/cache" "cache"
  clean_directory "${CURSOR_DIR}/CachedData" "CachedData"
  clean_directory "${CURSOR_DIR}/CachedExtensionVSIXs" "CachedExtensionVSIXs"
  clean_directory "${CURSOR_DIR}/Code Cache" "Code Cache"
  clean_directory "${CURSOR_DIR}/GPUCache" "GPUCache"
  clean_directory "${CURSOR_DIR}/logs" "logs"
  echo ""

  # Aggressive cleanup
  if [[ "${AGGRESSIVE}" == true ]]; then
    log_info "Aggressive cleanup (stale threshold: ${STALE_DAYS} days):"
    clean_directory "${CURSOR_DIR}/Backups" "Backups"
    clean_terminal_directories
    clean_stale_projects
    echo ""
  fi

  # Summary
  local freed_size
  freed_size=$(format_bytes $((TOTAL_SIZE * 1024)))

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  if [[ "${DRY_RUN}" == true ]]; then
    log_info "Summary (Dry Run):"
    log_info "  Would free: ${freed_size}"
  else
    log_success "Cleanup complete!"
    log_info "  Items cleaned: ${ITEMS_CLEANED}"
    log_info "  Space freed: ${freed_size}"

    # Show new size
    local new_size
    new_size=$(get_dir_size "${CURSOR_DIR}")
    log_info "  New ~/.cursor size: ${new_size}"
  fi
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

main "$@"
