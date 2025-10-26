#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export REPO_ROOT
export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"
VENV_PATH="${REPO_ROOT}/.venv"

if [[ -d "${VENV_PATH}" ]]; then
  # shellcheck source=/dev/null
  source "${VENV_PATH}/bin/activate"
fi

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command '$1' not found. Run 'make bootstrap'." >&2
    exit 1
  fi
}

pass_through_fix_flag() {
  local default_flag="$1"
  shift || true
  for arg in "$@"; do
    if [[ "$arg" == "--fix" ]]; then
      echo "--fix"
      return
    fi
  done
  if [[ -n "${default_flag}" ]]; then
    echo "${default_flag}"
  fi
}
