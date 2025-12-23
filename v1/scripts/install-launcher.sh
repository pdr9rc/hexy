#!/usr/bin/env bash
set -euo pipefail

OS_TYPE="${OSTYPE:-}"

if [[ "$OS_TYPE" == darwin* ]]; then
  # macOS paths
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  INSTALL_DIR="${HOME}/Library/Application Support/hexy"
  STATE_DIR="${HOME}/Library/Application Support/hexy"
  DESKTOP_DIR="${HOME}/Library/Application Support/hexy" # not used for .desktop
  ICON_DIR="${HOME}/Library/Application Support/hexy"
else
  # Linux paths (unchanged)
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  INSTALL_DIR="${HOME}/.local/opt/hexy"
  STATE_DIR="${HOME}/.local/share/hexy"
  DESKTOP_DIR="${HOME}/.local/share/applications"
  ICON_DIR="${HOME}/.local/share/icons"
fi

mkdir -p "${INSTALL_DIR}" "${STATE_DIR}" "${ICON_DIR}"

echo "📦 Installing Hexy into ${INSTALL_DIR}"

# Rsync repo into install dir (excluding VCS and node_modules caches)
rsync -a --delete \
  --exclude=".git/" \
  --exclude=".venv/" \
  --exclude="venv/" \
  --exclude="__pycache__/" \
  --exclude=".mypy_cache/" \
  --exclude="node_modules/" \
  --exclude="dist/" \
  "${REPO_DIR}/" "${INSTALL_DIR}/"

# Save app_dir to state so launchers work after repo is deleted
echo "${INSTALL_DIR}" > "${STATE_DIR}/app_dir"

# Install icon
if [ -f "${INSTALL_DIR}/backend/web/static/icons/icon-512.png" ]; then
  if [[ "$OS_TYPE" == darwin* ]]; then
    cp -f "${INSTALL_DIR}/backend/web/static/icons/icon-512.png" "${ICON_DIR}/hexy.png"
  else
    install -Dm644 "${INSTALL_DIR}/backend/web/static/icons/icon-512.png" "${ICON_DIR}/hexy.png"
  fi
fi

# Install launchers (copied into STATE_DIR so both OSes use same entrypoint)
install -Dm755 "${INSTALL_DIR}/scripts/hexy-backend.sh" "${STATE_DIR}/hexy-backend"
install -Dm755 "${INSTALL_DIR}/scripts/hexy-launcher.sh" "${STATE_DIR}/hexy-run"
install -Dm755 "${INSTALL_DIR}/scripts/hexy-electron.sh" "${STATE_DIR}/hexy-electron"

# Build Electron in install dir (node, ts)
(
  cd "${INSTALL_DIR}"
  echo "📥 Installing npm packages..."
  npm ci || npm install
  echo "🛠️  Building Electron main..."
  npm run build:electron
  # Vendor lottie-web into static for offline/Electron use
  if [ -f "node_modules/lottie-web/build/player/lottie.min.js" ]; then
    mkdir -p "backend/web/static/vendor"
    cp -f "node_modules/lottie-web/build/player/lottie.min.js" "backend/web/static/vendor/lottie.min.js"
  fi
)

# Install Python dependencies into venv under STATE_DIR
(
  echo "🐍 Setting up Python environment..."
  PY_BIN="python3"
  command -v python3 >/dev/null 2>&1 || PY_BIN="python"
  if command -v "$PY_BIN" >/dev/null 2>&1; then
    "$PY_BIN" -m venv "${STATE_DIR}/venv" || true
    if [ -f "${STATE_DIR}/venv/bin/activate" ]; then
      # shellcheck disable=SC1090
      . "${STATE_DIR}/venv/bin/activate"
      pip install --upgrade pip >/dev/null 2>&1 || true
      if [ -f "${INSTALL_DIR}/requirements.txt" ]; then
        echo "📦 Installing Python requirements..."
        pip install -r "${INSTALL_DIR}/requirements.txt" || pip install flask requests markdown
      else
        echo "📦 Installing minimal Python deps..."
        pip install flask requests markdown
      fi
      deactivate || true
    fi
  else
    echo "⚠️  python3 not found; backend script will try to install runtime deps."
  fi
)

if [[ "$OS_TYPE" == darwin* ]]; then
  # macOS minimal launcher shim (.command)
  mkdir -p "${HOME}/Applications"
  COMMAND_FILE="${HOME}/Applications/Hexy.command"
  cat > "${COMMAND_FILE}" <<EOF
#!/bin/bash
open -a Terminal "${STATE_DIR}/hexy-electron"
EOF
  chmod +x "${COMMAND_FILE}"
  echo "✅ Installed macOS launcher: ${COMMAND_FILE}"
  echo "📂 Installed app dir: ${INSTALL_DIR}"
  echo "🖼️  Icon: ${ICON_DIR}/hexy.png"
  echo "🚀 Launch via Spotlight: Hexy.command (or run: \"${STATE_DIR}/hexy-electron\")"
else
  # Linux desktop entry points to Electron launcher
  mkdir -p "${DESKTOP_DIR}"
  DESKTOP_FILE="${DESKTOP_DIR}/hexy.desktop"
  cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Name=Hexy - The Dying Lands
Comment=Hexy Desktop (Electron + Flask)
Exec=${STATE_DIR}/hexy-electron %u
Terminal=false
Type=Application
Icon=${ICON_DIR}/hexy.png
Categories=Game;Utility;
StartupWMClass=hexy
MimeType=x-scheme-handler/hexy;
Environment=ELECTRON_OZONE_PLATFORM_HINT=auto
EOF
  
  # Register URL scheme
  update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
  xdg-mime default hexy.desktop x-scheme-handler/hexy >/dev/null 2>&1 || true
  
  echo "✅ Installed launcher: ${DESKTOP_FILE}"
  echo "📂 Installed app dir: ${INSTALL_DIR}"
  echo "🖼️  Icon: ${ICON_DIR}/hexy.png"
  echo "🔗 URL handler registered: hexy://"
  echo "🚀 Run from menu or: ${STATE_DIR}/hexy-electron"
fi

