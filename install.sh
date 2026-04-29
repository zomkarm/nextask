#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Nextask — installer for Linux
# Usage:
#   ./install.sh             install
#   ./install.sh --uninstall remove everything
# ─────────────────────────────────────────────

set -e

APP_NAME="nextask"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

print_header() {
  echo ""
  echo "  ╔══════════════════════════════════╗"
  echo "  ║   Nextask  v1.0                  ║"
  echo "  ║   Minimal Task Execution System  ║"
  echo "  ╚══════════════════════════════════╝"
  echo ""
}

# ── Uninstall ─────────────────────────────────

if [[ "$1" == "--uninstall" ]]; then
  print_header
  echo "  Uninstalling Nextask..."
  rm -rf  "$INSTALL_DIR"
  rm -f   "$BIN_DIR/nextask"
  rm -f   "$DESKTOP_DIR/nextask.desktop"
  echo "  [✓] Nextask removed."
  echo "  Note: your task data at ~/.local/share/nextask/nextask.db"
  echo "        has been removed along with the app."
  echo ""
  exit 0
fi

# ── Install ───────────────────────────────────

print_header

# Python check
if ! command -v python3 &>/dev/null; then
  echo "  [ERROR] python3 not found."
  echo "  Run: sudo apt install python3 python3-pip"
  exit 1
fi

PYVER=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$PYVER" -lt 10 ]; then
  echo "  [ERROR] Python 3.10+ required."
  exit 1
fi
echo "  [✓] Python $(python3 --version)"

# pip check
if ! command -v pip3 &>/dev/null; then
  echo "  [ERROR] pip3 not found."
  echo "  Run: sudo apt install python3-pip"
  exit 1
fi
echo "  [✓] pip3 found"

# Dependencies
echo ""
echo "  Installing dependencies..."
pip3 install --user -r requirements.txt --quiet
echo "  [✓] PyQt6 installed"

# Copy files
echo ""
echo "  Installing to $INSTALL_DIR ..."
mkdir -p "$INSTALL_DIR"
cp -r main.py db.py ui.py styles.py assets requirements.txt "$INSTALL_DIR/"
echo "  [✓] Files copied"

# Launcher
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/nextask" << LAUNCHER
#!/usr/bin/env bash
cd "$INSTALL_DIR"
python3 main.py "\$@"
LAUNCHER
chmod +x "$BIN_DIR/nextask"
echo "  [✓] Launcher: $BIN_DIR/nextask"

# Desktop entry
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/nextask.desktop" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=Nextask
Comment=Minimal Task Execution System
Exec=$BIN_DIR/nextask
Icon=$INSTALL_DIR/assets/icon.png
Terminal=false
Categories=Utility;Productivity;
Keywords=task;todo;productivity;
DESKTOP
echo "  [✓] Desktop entry created"

# PATH check
echo ""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "  [!] Add this to your ~/.bashrc then run: source ~/.bashrc"
  echo ""
  echo "      export PATH=\"\$HOME/.local/bin:\$PATH\""
  echo ""
else
  echo "  [✓] $BIN_DIR is in PATH"
fi

echo "  ────────────────────────────────────"
echo "  Done!"
echo ""
echo "  Run with: nextask"
echo "  Or find Nextask in your applications menu."
echo ""
echo "  Uninstall: ./install.sh --uninstall"
echo ""