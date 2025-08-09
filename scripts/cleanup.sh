#!/bin/bash

# Hexy Cleanup Script
# Removes old launcher files and processes

set -euo pipefail

echo "🧹 Cleaning up Hexy installation..."

# Kill any running processes
echo "🔄 Stopping running processes..."
pkill -f "hexy\|backend.run" 2>/dev/null || true
sleep 2

# Remove old launcher files
echo "🗑️  Removing old launcher files..."
rm -f ~/.local/share/hexy/hexy-run
rm -f ~/.local/share/hexy/hexy-backend
rm -f ~/.local/share/hexy/browser
rm -f ~/.local/share/hexy/port
rm -f ~/.local/share/hexy/backend.pid

# Remove old desktop files
echo "🗑️  Removing old desktop files..."
rm -f ~/.local/share/applications/hexy.desktop
rm -f ~/.local/share/applications/hexy-url.desktop

# Remove old systemd service
echo "🗑️  Removing old systemd service..."
rm -f ~/.config/systemd/user/hexy.service
systemctl --user daemon-reload 2>/dev/null || true

# Remove cache and temporary files
echo "🗑️  Removing cache files..."
rm -f /tmp/hexy-*.log
rm -rf ~/.local/share/hexy/chromium-profile

# Update desktop database
echo "🔄 Updating desktop database..."
update-desktop-database ~/.local/share/applications 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "To reinstall with Electron app, run:"
echo "  ./scripts/install-launcher.sh"
