#!/usr/bin/env bash
#
# Script Name     : golangci_lint.sh
#
# Purpose         : Run golangci-lint as a repo-managed pre-commit hook.
#                   - Lint changed Go code, or validate .golangci.yaml when
#                     called with --config-verify.
#                   - Skip cleanly when golangci-lint is absent or too old, so a
#                     repo without Go tooling is never blocked from committing.
#
#                   The upstream golangci-lint pre-commit hooks are deliberately
#                   not used. They declare `language: golang`, which makes
#                   pre-commit build the linter from source; that ran past eight
#                   minutes without finishing here. Worse, the upstream
#                   config-verify hook matches .golangci.yaml itself, so every
#                   repo generated from this scaffold would pay that build even
#                   with no Go code at all. Calling an installed binary takes
#                   about 50ms.
#
# Usage           : scripts/pre-commit/golangci_lint.sh [--config-verify]
#
#                   Invoked by .pre-commit-config.yaml, not usually by hand.
#
# Dependencies    : golangci-lint 2.x (optional; the hook skips without it)
#
# Exit Codes      : 0 success, or a clean skip when golangci-lint is unusable
#                   otherwise the exit code from golangci-lint
#
# ----------------------------------------------------------------------------
# Turn debug on or off
# set -x
# PS4='+ $(date "+%T") ${BASH_SOURCE##*/}:$LINENO: '
# ----------------------------------------------------------------------------

set -euo pipefail

# .golangci.yaml declares `version: "2"`, which golangci-lint 1.x cannot parse.
readonly REQUIRED_MAJOR_VERSION=2
readonly INSTALL_HINT='https://golangci-lint.run/docs/welcome/install/'

CONFIG_VERIFY=0

log() {
  printf '[golangci-lint] %s\n' "$*" >&2
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --config-verify)
        CONFIG_VERIFY=1
        shift
        ;;
      *)
        # pre-commit may still append file names even with pass_filenames off in
        # some invocations; ignore them rather than failing the commit.
        shift
        ;;
    esac
  done
}

# Returns non-zero when the linter cannot be used, which the caller treats as a
# skip rather than a failure: enforcement belongs to CI, and a missing local tool
# should not block a commit.
linter_is_usable() {
  local version_output major

  if ! command -v golangci-lint > /dev/null 2>&1; then
    log 'golangci-lint is not on PATH; skipping'
    log "install it: ${INSTALL_HINT}"
    return 1
  fi

  version_output="$(golangci-lint --version 2>&1 || true)"

  # "golangci-lint has version 2.12.2 built with go1.26.2 from ..."
  major="$(printf '%s\n' "${version_output}" \
    | sed -n 's/.*version v\{0,1\}\([0-9]\{1,\}\)\..*/\1/p' | head -1)"

  if [[ -z "${major}" ]]; then
    log "could not parse a version from: ${version_output}"
    log 'continuing anyway'
    return 0
  fi

  if ((major < REQUIRED_MAJOR_VERSION)); then
    log "golangci-lint ${major}.x is installed, but .golangci.yaml declares"
    log "schema version ${REQUIRED_MAJOR_VERSION}; skipping"
    log "upgrade it: ${INSTALL_HINT}"
    return 1
  fi
}

main() {
  parse_args "$@"

  if ! linter_is_usable; then
    exit 0
  fi

  if [[ "${CONFIG_VERIFY}" == 1 ]]; then
    log 'verifying .golangci.yaml'
    golangci-lint config verify
    log 'configuration is valid'
    return 0
  fi

  # Mirrors the upstream hook: only issues newer than HEAD, with autofix, so a
  # pre-existing backlog does not block unrelated commits.
  log 'linting changed Go code'
  golangci-lint run --new-from-rev HEAD --fix
}

main "$@"
