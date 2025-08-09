#!/usr/bin/env bash
set -euo pipefail

# Hexy desktop launcher: boots the local backend and opens the app

APP_NAME="Hexy - The Dying Lands"
STATE_DIR="${HOME}/.local/share/hexy"
# Prefer installed app_dir if present, otherwise fallback to repo-relative
if [ -f "${STATE_DIR}/app_dir" ]; then
  APP_DIR="$(cat "${STATE_DIR}/app_dir")"
else
  APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi
BACKEND_BIN="${STATE_DIR}/hexy-backend"
PORT_FILE="${STATE_DIR}/port"
ICON_DST="${HOME}/.local/share/icons/hexy.png"
LOG_FILE="/tmp/hexy-launcher.log"
PIDFILE="${STATE_DIR}/backend.pid"
BACK_LOG="/tmp/hexy-backend.log"
BROWSER_MODE=""

mkdir -p "${STATE_DIR}"

log() { printf '%s %s\n' "$(date +'%F %T')" "$*" >>"${LOG_FILE}"; }
log "Launcher start"

# Copy icon if present in repo
if [ -f "${APP_DIR}/backend/web/static/icons/icon-512.png" ]; then
  install -Dm644 "${APP_DIR}/backend/web/static/icons/icon-512.png" "${ICON_DST}"
fi

# Use a fixed port unless overridden by HEXY_PORT
PORT=${HEXY_PORT:-7777}
# Extend idle timeout to 30 minutes by default
export HEXY_IDLE_TIMEOUT=${HEXY_IDLE_TIMEOUT:-1800}
echo -n "${PORT}" > "${PORT_FILE}"
log "Using fixed PORT=${PORT}"

# Start backend only if port is not already in use
is_listening() { ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${PORT}$"; }
if ! is_listening; then
# If a previous backend is running on this port, stop it first
if [ -f "${PIDFILE}" ] && kill -0 "$(cat "${PIDFILE}")" >/dev/null 2>&1; then
  log "Stopping previous backend PID=$(cat "${PIDFILE}")"
  kill "$(cat "${PIDFILE}")" >/dev/null 2>&1 || true
  sleep 0.5
fi

HEXY_PORT="${PORT}" "${BACKEND_BIN}" >/tmp/hexy-backend.log 2>&1 &
  BACK_PID=$!
  log "Started backend PID=${BACK_PID}"
else
  log "Backend already listening on ${PORT}, not starting a new one"
fi

# Wait for backend to be ready (up to 20s)
READY=0
is_up() {
  local url="http://127.0.0.1:${PORT}/"
  if command -v curl >/dev/null 2>&1; then
    curl -sSf "$url" >/dev/null 2>&1 && return 0 || return 1
  elif command -v python3 >/dev/null 2>&1; then
    python3 - "$url" <<'PY' 2>/dev/null
import sys, urllib.request
try:
    urllib.request.urlopen(sys.argv[1], timeout=1)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
    return $?
  else
    # Fallback: /dev/tcp if available
    (exec 3<>/dev/tcp/127.0.0.1/${PORT}) >/dev/null 2>&1 && { exec 3>&- 3<&-; return 0; } || return 1
  fi
}
for i in $(seq 1 60); do
  if is_up; then READY=1; break; fi
  sleep 0.5
done
log "Backend ready=${READY}"

# Open app window preferring Chromium/Chrome app mode (no tabs). Fallback to xdg-open.
APP_URL="http://127.0.0.1:${PORT}/"
PROFILE_DIR="${STATE_DIR}/chromium-profile"
mkdir -p "${PROFILE_DIR}"

open_chromium() {
  local bin="$1"
  nohup "$bin" --user-data-dir="${PROFILE_DIR}" --app="${APP_URL}" --new-window --no-first-run >/dev/null 2>&1 &
}

open_chromium_flatpak() {
  local appid="$1" # e.g., org.chromium.Chromium
  nohup flatpak run "$appid" --app="${APP_URL}" --new-window --no-first-run >/dev/null 2>&1 &
}

# Allow user override via env or config file
if [ -z "${HEXY_BROWSER:-}" ] && [ -f "${STATE_DIR}/browser" ]; then
  HEXY_BROWSER="$(cat "${STATE_DIR}/browser")"
fi

# Honor explicit override
if [ -n "${HEXY_BROWSER:-}" ]; then
  log "Using HEXY_BROWSER='${HEXY_BROWSER}'"
  nohup ${HEXY_BROWSER} --app="${APP_URL}" --new-window --no-first-run >/dev/null 2>&1 &
  BROWSER_MODE="chromium"
elif command -v chromium >/dev/null 2>&1; then
  log "Using chromium"
  open_chromium chromium
  BROWSER_MODE="chromium"
elif command -v chromium-browser >/dev/null 2>&1; then
  log "Using chromium-browser"
  open_chromium chromium-browser
  BROWSER_MODE="chromium"
elif command -v flatpak >/dev/null 2>&1 && flatpak info org.chromium.Chromium >/dev/null 2>&1; then
  log "Using flatpak org.chromium.Chromium"
  open_chromium_flatpak org.chromium.Chromium
  BROWSER_MODE="chromium"
elif command -v google-chrome >/dev/null 2>&1; then
  log "Using google-chrome"
  open_chromium google-chrome
  BROWSER_MODE="chromium"
elif command -v google-chrome-stable >/dev/null 2>&1; then
  log "Using google-chrome-stable"
  open_chromium google-chrome-stable
  BROWSER_MODE="chromium"
elif command -v brave >/dev/null 2>&1; then
  log "Using brave"
  open_chromium brave
  BROWSER_MODE="chromium"
elif command -v brave-browser >/dev/null 2>&1; then
  log "Using brave-browser"
  open_chromium brave-browser
  BROWSER_MODE="chromium"
else
  log "Fallback to xdg-open"
  setsid xdg-open "${APP_URL}" >/dev/null 2>&1 &
  BROWSER_MODE="xdgopen"
fi

# Do NOT open a second window/tab if Chromium branch was used

# Do not wait; allow launcher to exit while backend keeps running
exit 0


