#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .venv/bin/activate ]]; then
  echo "Virtual env not found at .venv. Create it with: uv sync" >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python UI/HomePage.py
