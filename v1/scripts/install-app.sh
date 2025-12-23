#!/usr/bin/env bash
set -euo pipefail

# Installer: copies the app to a chosen directory, registers launcher, writes app_dir override,
# optionally sets a Chromium-based browser override and launches the app.

DEFAULT_DIR="$HOME/.local/opt/hexy"
TARGET_DIR=""
DO_LAUNCH=0

# Parse simple flags: --dir=PATH or -d PATH, --launch
for arg in "$@"; do
  case "$arg" in
    --dir=*) TARGET_DIR="${arg#*=}" ;;
    -d) shift; TARGET_DIR="${1:-}" ;;
    --launch) DO_LAUNCH=1 ;;
  esac
done

if [ -z "${TARGET_DIR}" ]; then
  read -rp "Install Hexy to which directory? [${DEFAULT_DIR}]: " TARGET_DIR
  TARGET_DIR=${TARGET_DIR:-$DEFAULT_DIR}
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="$HOME/.local/share/hexy"
DESKTOP_DIR="$HOME/.local/share/applications"

mkdir -p "$TARGET_DIR" "$STATE_DIR" "$DESKTOP_DIR"

echo "Copying files to ${TARGET_DIR}..."
rsync -a --delete --exclude .git --exclude venv --exclude __pycache__ "$SRC_DIR/" "$TARGET_DIR/"

# Point runtime to the chosen install dir
printf '%s' "$TARGET_DIR" > "$STATE_DIR/app_dir"
echo "Wrote app_dir override -> $TARGET_DIR"
echo "Disabling service worker for launcher to avoid cache during development..."
echo "1" > "$STATE_DIR/no_sw" || true

echo "Installing launcher..."
bash "$TARGET_DIR/scripts/install-launcher.sh"

# Best-effort: set a Chromium-based browser override if not present
if [ ! -f "$STATE_DIR/browser" ]; then
  if command -v chromium >/dev/null 2>&1; then echo chromium > "$STATE_DIR/browser";
  elif command -v chromium-browser >/dev/null 2>&1; then echo chromium-browser > "$STATE_DIR/browser";
  elif command -v google-chrome >/dev/null 2>&1; then echo google-chrome > "$STATE_DIR/browser";
  elif command -v brave-browser >/dev/null 2>&1; then echo brave-browser > "$STATE_DIR/browser";
  elif command -v brave >/dev/null 2>&1; then echo brave > "$STATE_DIR/browser";
  elif command -v flatpak >/dev/null 2>&1 && flatpak info org.chromium.Chromium >/dev/null 2>&1; then echo 'flatpak run org.chromium.Chromium' > "$STATE_DIR/browser"; fi
fi

echo "Hexy installed to ${TARGET_DIR}. Launcher: ~/.local/share/hexy/hexy-run"

# Optional: stop any previous backend and launch now
if [ "$DO_LAUNCH" -eq 1 ]; then
  PIDFILE="$STATE_DIR/backend.pid"
  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
    sleep 0.5
  fi
  ~/.local/share/hexy/hexy-run >/dev/null 2>&1 &
  echo "Launched Hexy in background. You can also open: ~/.local/share/hexy/hexy-run"
fi

echo "Bootstrapping Dying Lands output in installed directory..."
bash "$TARGET_DIR/scripts/bootstrap-output.sh" || true


