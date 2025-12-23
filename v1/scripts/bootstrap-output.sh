#!/usr/bin/env bash
set -euo pipefail

# Generate The Dying Lands output inside the installed app directory

STATE_DIR="${HOME}/.local/share/hexy"
LANG_OPT="${1:-}"

# Resolve APP_DIR (prefer installer-set app_dir)
if [ -f "${STATE_DIR}/app_dir" ]; then
  APP_DIR="$(cat "${STATE_DIR}/app_dir")"
else
  APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

VENVDIR="${STATE_DIR}/venv"

run_generator() {
  local lang_arg="$1"
  PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}" python3 - "$lang_arg" <<'PY'
import sys
from backend.config import get_config
from backend.main_map_generator import MainMapGenerator

language = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else 'en'
cfg = get_config()
cfg.paths.output_path.mkdir(parents=True, exist_ok=True)
gen = MainMapGenerator({'language': language})
gen.generate_full_map()
print(f"Generated output at {cfg.paths.output_path} for language={language}")
PY
}

# Create venv if possible; fallback to system python
if python3 -m venv --help >/dev/null 2>&1; then
  if [ ! -d "${VENVDIR}" ]; then
    python3 -m venv "${VENVDIR}"
  fi
  if [ -f "${VENVDIR}/bin/activate" ]; then
    # shellcheck disable=SC1090
    source "${VENVDIR}/bin/activate"
    pip install --upgrade pip >/dev/null 2>&1 || true
    if [ -f "${APP_DIR}/requirements.txt" ]; then
      pip install -r "${APP_DIR}/requirements.txt"
    else
      pip install flask >/dev/null 2>&1 || true
    fi
    run_generator "${LANG_OPT}"
    exit 0
  fi
fi

# Fallback: system python
run_generator "${LANG_OPT}"


