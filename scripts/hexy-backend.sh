#!/usr/bin/env bash
set -euo pipefail

# Start Hexy backend only (no browser). Designed for systemd --user service.

STATE_DIR="${HOME}/.local/share/hexy"
PIDFILE="${STATE_DIR}/backend.pid"
# Prefer installed app_dir if present, otherwise fallback to repo-relative
if [ -f "${STATE_DIR}/app_dir" ]; then
  APP_DIR="$(cat "${STATE_DIR}/app_dir")"
else
  APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
VENVDIR="${STATE_DIR}/venv"
PORT="${HEXY_PORT:-7777}"

mkdir -p "${STATE_DIR}"
export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
export HEXY_APP_DIR="${APP_DIR}"
export HEXY_OUTPUT_DIR="${APP_DIR}/dying_lands_output"
export HEXY_PORT="${PORT}"
echo $$ > "${PIDFILE}" 2>/dev/null || true

use_system_python() {
  command -v python3 >/dev/null 2>&1 || { echo "[hexy] python3 not found" >&2; exit 1; }
  # Best-effort deps
  python3 - <<'PY'
import importlib, subprocess, sys
mods = ['flask']
for m in mods:
    try:
        importlib.import_module(m)
    except Exception:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', m])
PY
  exec python3 -m backend.run
}

if python3 -m venv --help >/dev/null 2>&1; then
  if [ ! -d "${VENVDIR}" ]; then
    python3 -m venv "${VENVDIR}" || use_system_python
  fi
  if [ -f "${VENVDIR}/bin/activate" ]; then
    source "${VENVDIR}/bin/activate"
    pip install --upgrade pip >/dev/null 2>&1 || true
    if [ -f "${APP_DIR}/requirements.txt" ]; then
      pip install -r "${APP_DIR}/requirements.txt" || pip install flask
    else
      pip install flask || true
    fi
    exec python -m backend.run
  fi
fi

# Fallback: system python
use_system_python


