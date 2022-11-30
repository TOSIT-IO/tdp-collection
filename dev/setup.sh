#!/usr/bin/env bash

set -euo pipefail

readonly PYTHON_BIN=${PYTHON_BIN:-python3}
readonly PYTHON_VENV=${PYTHON_VENV:-venv}

setup_python_venv() {
  if [[ ! -d "$PYTHON_VENV" ]]; then
    echo "Create python venv with '${PYTHON_BIN}' to '${PYTHON_VENV}' and update pip to latest version"
    "$PYTHON_BIN" -m venv "$PYTHON_VENV"
    (
      source "${PYTHON_VENV}/bin/activate"
      pip install -U pip
    )
  else
    echo "Python venv '${PYTHON_VENV}' already exists, nothing to do"
  fi
  echo "Install python dependencies"
  (
    source "${PYTHON_VENV}/bin/activate"
    pip install -r dev/requirements.txt
    pre-commit install
  )
  return 0
}

main() {
  setup_python_venv
}

main "$@"
