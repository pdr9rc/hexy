#!/bin/bash

# Hexy Electron Desktop Launcher
# Starts the Flask backend and launches the Electron app

set -euo pipefail

# OS-aware state dir
if [[ "${OSTYPE:-}" == darwin* ]]; then
  STATE_DIR="${HOME}/Library/Application Support/hexy"
else
  STATE_DIR="${HOME}/.local/share/hexy"
fi

APP_DIR=""

# Prefer installed app_dir if present, otherwise fallback to repo-relative
if [ -f "${STATE_DIR}/app_dir" ]; then
  APP_DIR="$(cat "${STATE_DIR}/app_dir")"
else
  APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

cd "${APP_DIR}"

echo "🚀 Starting Hexy Desktop App..."

# Kill any existing backend processes
pkill -f "python.*-m backend.run" 2>/dev/null || true
sleep 1

# Start the backend
echo "📡 Starting Flask backend..."
cd "${APP_DIR}"
export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
export HEXY_APP_DIR="${APP_DIR}"

# Decide output dir: migrate to STATE_DIR if present, else fallback to APP_DIR to avoid breakage
OUTPUT_STATE="${STATE_DIR}/dying_lands_output"
OUTPUT_APP="${APP_DIR}/dying_lands_output"
# If app output exists and state output missing, migrate once
if [ -d "${OUTPUT_APP}/hexes" ] && [ ! -d "${OUTPUT_STATE}/hexes" ]; then
  mkdir -p "${OUTPUT_STATE}"
  rsync -a "${OUTPUT_APP}/" "${OUTPUT_STATE}/" || true
fi
# Prefer state output if it looks valid, else fallback to app output
if [ -d "${OUTPUT_STATE}/hexes" ]; then
  export HEXY_OUTPUT_DIR="${OUTPUT_STATE}"
else
  export HEXY_OUTPUT_DIR="${OUTPUT_APP}"
fi

HEXY_PORT=7777 python3 -m backend.run >/tmp/hexy-backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:7777/api/health >/dev/null 2>&1; then
    echo "✅ Backend is ready!"
    break
  fi
  echo "   Attempt $i/30..."
  sleep 1
done

# Start Electron app (disable sandbox for unprivileged runs)
echo "🖥️  Starting Electron app..."
cd "${APP_DIR}"
ELECTRON_BIN="${APP_DIR}/node_modules/.bin/electron"
if [ ! -x "$ELECTRON_BIN" ]; then
  echo "❌ Electron binary not found at $ELECTRON_BIN"
  echo "Tip: Re-run installer or run: npm install && npm run build:electron"
  kill "$BACKEND_PID" 2>/dev/null || true
  exit 1
fi
# Hint Electron/Chromium to auto-select the appropriate platform backend (Wayland/X11)
export ELECTRON_OZONE_PLATFORM_HINT=${ELECTRON_OZONE_PLATFORM_HINT:-auto}
"$ELECTRON_BIN" "${APP_DIR}/dist/electron/main.js" --no-sandbox --disable-setuid-sandbox

# Cleanup when Electron exits
echo "🧹 Cleaning up..."
kill $BACKEND_PID 2>/dev/null || true
