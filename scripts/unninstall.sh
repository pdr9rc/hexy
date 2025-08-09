systemctl --user disable --now hexy.service >/dev/null 2>&1 || true
rm -f "$HOME/.config/systemd/user/hexy.service"
pkill -f hexy-backend || true
rm -rf "$HOME/.local/share/hexy" \
       "$HOME/.local/share/applications/hexy.desktop" \
       "$HOME/.local/share/icons/hexy.png" \
       /tmp/hexy-backend.log /tmp/hexy-launcher.log
update-desktop-database >/dev/null 2>&1 || true