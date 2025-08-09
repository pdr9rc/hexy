#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${HOME}/.local/share/hexy"
DESKTOP_DIR="${HOME}/.local/share/applications"

mkdir -p "${BIN_DIR}" "${DESKTOP_DIR}"

# Install runner
install -Dm755 "${APP_DIR}/scripts/hexy-launcher.sh" "${BIN_DIR}/hexy-run"
install -Dm755 "${APP_DIR}/scripts/hexy-backend.sh" "${BIN_DIR}/hexy-backend"

# Install icon if present
if [ -f "${APP_DIR}/backend/web/static/icons/icon-512.png" ]; then
  install -Dm644 "${APP_DIR}/backend/web/static/icons/icon-512.png" "${HOME}/.local/share/icons/hexy.png"
fi

# Install desktop entry
DESKTOP_FILE="${DESKTOP_DIR}/hexy.desktop"
cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Name=Hexy - The Dying Lands
Comment=Run Hexy locally (backend + app)
Exec=${BIN_DIR}/hexy-run
Terminal=false
Type=Application
Icon=${HOME}/.local/share/icons/hexy.png
Categories=Game;Utility;
EOF

update-desktop-database >/dev/null 2>&1 || true
echo "Installed launcher: ${DESKTOP_FILE}"

# Register custom URL scheme to allow frontend to trigger launcher
URL_HANDLER_FILE="${DESKTOP_DIR}/hexy-url.desktop"
cat > "${URL_HANDLER_FILE}" <<EOF
[Desktop Entry]
Name=Hexy URL Launcher
Exec=${BIN_DIR}/hexy-run %u
Terminal=false
Type=Application
NoDisplay=true
MimeType=x-scheme-handler/hexy;
EOF
update-desktop-database >/dev/null 2>&1 || true
xdg-mime default hexy-url.desktop x-scheme-handler/hexy >/dev/null 2>&1 || true
echo "Registered URL scheme: hexy://"

# Ensure app_dir points to installed location if not explicitly set by install-app.sh
if [ ! -f "${BIN_DIR}/../share/hexy/app_dir" ] && [ ! -f "${HOME}/.local/share/hexy/app_dir" ]; then
  mkdir -p "${HOME}/.local/share/hexy"
  echo "${APP_DIR}" > "${HOME}/.local/share/hexy/app_dir"
fi

# Optional: systemd --user service for backend auto-start
if command -v systemctl >/dev/null 2>&1; then
  SVC_DIR="${HOME}/.config/systemd/user"
  mkdir -p "${SVC_DIR}"
  SVC_FILE="${SVC_DIR}/hexy.service"
  cat > "${SVC_FILE}" <<EOS
[Unit]
Description=Hexy Backend
After=network.target

[Service]
Type=simple
Environment=HEXY_PORT=6660
ExecStart=${BIN_DIR}/hexy-backend
Restart=on-failure

[Install]
WantedBy=default.target
EOS
  systemctl --user daemon-reload || true
  echo "Optional: enable backend auto-start with: systemctl --user enable --now hexy.service"
fi

