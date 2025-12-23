#!/bin/bash

# Hexy Cleanup Script
# Removes old launcher files and processes

set -euo pipefail

STATE_DIR="${HOME}/.local/share/hexy"
APP_DIR="${HOME}/.local/opt/hexy"

PURGE_OUTPUT=false
PURGE_APP=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --purge-output) PURGE_OUTPUT=true; shift ;;
    --purge-app) PURGE_APP=true; shift ;;
    *) shift ;;
  esac
done

echo "🧹 Cleaning up Hexy installation..."

# Kill any running processes (backend or electron launcher)
echo "🔄 Stopping running processes..."
pkill -f "hexy-electron" 2>/dev/null || true
pkill -f "backend.run" 2>/dev/null || true
pkill -f "python3 .*backend/run.py" 2>/dev/null || true
# Also kill anything listening on 7777 (launcher default)
PIDS=$(ss -ltnp 2>/dev/null | awk '/:7777 /{print $NF}' | sed -n 's/.*pid=\([0-9]*\).*/\1/p' | sort -u)
if [[ -n "${PIDS}" ]]; then
  echo "   Killing PIDs on :7777 → ${PIDS}"
  xargs -r -n1 kill <<<"${PIDS}" 2>/dev/null || true
  sleep 1
fi

# Remove launcher state files
echo "🗑️  Removing launcher state files..."
rm -f "${STATE_DIR}/hexy-run" || true
rm -f "${STATE_DIR}/hexy-backend" || true
rm -f "${STATE_DIR}/browser" || true
rm -f "${STATE_DIR}/port" || true
rm -f "${STATE_DIR}/backend.pid" || true
rm -f "${STATE_DIR}/app_dir" || true

# Remove desktop entries
echo "🗑️  Removing desktop files..."
rm -f "${HOME}/.local/share/applications/hexy.desktop" || true
rm -f "${HOME}/.local/share/applications/hexy-url.desktop" || true

# Remove user systemd service
echo "🗑️  Removing user systemd service..."
rm -f "${HOME}/.config/systemd/user/hexy.service" || true
systemctl --user daemon-reload 2>/dev/null || true

# Remove cache and temporary files
echo "🗑️  Removing cache files..."
rm -f /tmp/hexy-*.log || true
rm -rf "${STATE_DIR}/chromium-profile" || true

# Optional purges
if ${PURGE_OUTPUT}; then
  echo "⚠️  Purging output directory: ${STATE_DIR}/dying_lands_output"
  rm -rf "${STATE_DIR}/dying_lands_output" || true
fi
if ${PURGE_APP}; then
  echo "⚠️  Purging installed app directory: ${APP_DIR}"
  rm -rf "${APP_DIR}" || true
fi

# Update desktop database
echo "🔄 Updating desktop database..."
update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "To reinstall the Electron launcher, run:"
echo "  ./scripts/install-launcher.sh"
echo ""
echo "Tips:"
echo "- To remove the permanent output as well, run: scripts/cleanup.sh --purge-output"
echo "- To remove the installed app files too, run: scripts/cleanup.sh --purge-app"
