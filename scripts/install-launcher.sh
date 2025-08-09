#!/usr/bin/env bash
set -euo pipefail

# Self-contained installer to ~/.local/opt/hexy
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_DIR="${HOME}/.local/opt/hexy"
STATE_DIR="${HOME}/.local/share/hexy"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons"

mkdir -p "${INSTALL_DIR}" "${STATE_DIR}" "${DESKTOP_DIR}" "${ICON_DIR}"

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
  install -Dm644 "${INSTALL_DIR}/backend/web/static/icons/icon-512.png" "${ICON_DIR}/hexy.png"
fi

# Install launchers
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
)

# Desktop entry points to Electron launcher
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
EOF

# Optional separate URL handler entry (hidden), also pointing to hexy-electron
URL_HANDLER_FILE="${DESKTOP_DIR}/hexy-url.desktop"
cat > "${URL_HANDLER_FILE}" <<EOF
[Desktop Entry]
Name=Hexy URL Handler
Exec=${STATE_DIR}/hexy-electron %u
Terminal=false
Type=Application
NoDisplay=true
MimeType=x-scheme-handler/hexy;
EOF

# Register URL scheme
update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
xdg-mime default hexy.desktop x-scheme-handler/hexy >/dev/null 2>&1 || true

echo "✅ Installed launcher: ${DESKTOP_FILE}"
echo "📂 Installed app dir: ${INSTALL_DIR}"
echo "🖼️  Icon: ${ICON_DIR}/hexy.png"
echo "🔗 URL handler registered: hexy://"
echo "🚀 Run from menu or: ${STATE_DIR}/hexy-electron"

