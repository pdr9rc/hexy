#!/usr/bin/env bash
set -euo pipefail

# Minimal Debian package builder using fpm
# Requires: ruby-dev, build-essential, fpm (gem install fpm)

APP_NAME="hexy"
VERSION="0.1.0"
STAGE="/tmp/${APP_NAME}-pkg"
PREFIX="/opt/${APP_NAME}"

rm -rf "$STAGE" && mkdir -p "$STAGE${PREFIX}"

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rsync -a --delete --exclude .git --exclude venv --exclude __pycache__ "$SRC_DIR/" "$STAGE${PREFIX}/"

# Desktop integration
mkdir -p "$STAGE/usr/share/applications" "$STAGE/usr/share/icons/hicolor/512x512/apps" "$STAGE/usr/bin"
install -Dm644 "$SRC_DIR/backend/web/static/icons/icon-512.png" "$STAGE/usr/share/icons/hicolor/512x512/apps/${APP_NAME}.png"
cat > "$STAGE/usr/share/applications/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Name=Hexy - The Dying Lands
Comment=Run Hexy locally (backend + app)
Exec=/usr/bin/${APP_NAME}
Terminal=false
Type=Application
Icon=${APP_NAME}
Categories=Game;Utility;
EOF

# Wrapper to run launcher from installed prefix
cat > "$STAGE/usr/bin/${APP_NAME}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
STATE_DIR="$HOME/.local/share/hexy"
mkdir -p "$STATE_DIR"
echo "/opt/hexy" > "$STATE_DIR/app_dir"
"$STATE_DIR/hexy-run" >/dev/null 2>&1 || true
if [ ! -x "$STATE_DIR/hexy-run" ]; then
  bash /opt/hexy/scripts/install-launcher.sh >/dev/null 2>&1 || true
fi
exec "$HOME/.local/share/hexy/hexy-run"
EOF
chmod +x "$STAGE/usr/bin/${APP_NAME}"

echo "Building .deb with fpm..."
fpm -s dir -t deb -n "$APP_NAME" -v "$VERSION" -C "$STAGE" \
  --deb-no-default-config-files \
  --description "Hexy - The Dying Lands" \
  --license "MIT" \
  --vendor "Hexy" \
  --url "https://example.com" \
  .

echo "Done. Generated .deb in current directory."


