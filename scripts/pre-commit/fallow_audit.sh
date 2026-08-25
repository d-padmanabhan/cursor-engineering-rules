#!/usr/bin/env bash
set -euo pipefail

# Fallow changed-code audit for local commits.
#
# Keep this as a repo-managed pre-commit hook instead of running
# `fallow hooks install --target git`, so all hooks remain visible in
# `.pre-commit-config.yaml` and reproducible for every contributor.
#
# Purpose:
#   - Run Fallow's changed-code audit before a commit.
#   - Surface newly introduced dead code, duplication, circular dependencies,
#     and complexity hotspots early.
#   - Compare the current branch to the merge-base of its upstream branch when
#     possible, falling back to `main` for branches without upstream tracking.
#
# Support notes:
#   - This script logs its decision points with a `[fallow-audit]` prefix so
#     engineers can debug hook behavior from pre-commit output.
#   - It exits 0 when the repo has no package.json or no installed Fallow, so
#     scaffolded repos that do not use Fallow are not blocked from committing.
#   - It prefers a local `pnpm` binary, falls back to Corepack, and finally
#     falls back to `npx --yes pnpm@<packageManager-version>` so new machines can
#     still run the hook before pnpm is globally installed.
#   - Fallow findings are emitted by `pnpm exec fallow audit --quiet`.

log() {
  printf '[fallow-audit] %s\n' "$*" >&2
}

started_at_epoch="$(date +%s)"
log "starting changed-code audit"

# Skip cleanly in repos that do not use Fallow. A freshly scaffolded repo has no
# package.json, and `pnpm exec` fails there, which would block every commit.
if [[ ! -f package.json ]]; then
  log "no package.json in repo root; skipping audit"
  exit 0
fi

if [[ ! -x node_modules/.bin/fallow ]]; then
  log "fallow is not installed in node_modules/.bin; skipping audit"
  log "install it with: pnpm add -D fallow"
  exit 0
fi

pnpm_cmd=()

if command -v pnpm > /dev/null 2>&1; then
  pnpm_cmd=(pnpm)
  log "pnpm: $(command -v pnpm)"
elif command -v corepack > /dev/null 2>&1; then
  pnpm_cmd=(corepack pnpm)
  log "pnpm not found on PATH; using Corepack pnpm"
elif command -v npx > /dev/null 2>&1; then
  package_manager="$(node -p "require('./package.json').packageManager || ''" 2> /dev/null || true)"
  pnpm_version="${package_manager#pnpm@}"
  if [[ -z "${pnpm_version}" || "${pnpm_version}" == "${package_manager}" ]]; then
    pnpm_version="11.17.0"
  fi
  pnpm_cmd=(npx --yes "pnpm@${pnpm_version}")
  log "pnpm not found on PATH; using transient npx pnpm@${pnpm_version}"
else
  log "pnpm, corepack, and npx are unavailable; skipping audit"
  exit 0
fi

upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2> /dev/null || true)"

if [[ -n "${upstream}" ]]; then
  base="$(git merge-base "${upstream}" HEAD 2> /dev/null || echo "${upstream}")"
  log "upstream: ${upstream}"
  log "base: ${base}"
elif git rev-parse --verify --quiet main > /dev/null; then
  base="main"
  log "no upstream branch detected; using fallback base: ${base}"
else
  # Repos on a differently named default branch, and repos before their first
  # commit, have no ref to diff against. Skip rather than fail the commit.
  log "no upstream branch and no local 'main' ref; skipping audit"
  exit 0
fi

log "command: ${pnpm_cmd[*]} exec fallow audit --base ${base} --quiet"

set +e
"${pnpm_cmd[@]}" exec fallow audit --base "${base}" --quiet
status=$?
set -e

finished_at_epoch="$(date +%s)"
duration_seconds=$((finished_at_epoch - started_at_epoch))

if [[ "${status}" -eq 0 ]]; then
  log "completed successfully in ${duration_seconds}s"
else
  log "failed with exit code ${status} after ${duration_seconds}s"
fi

exit "${status}"
