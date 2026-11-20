#!/usr/bin/env bash
# piphone setup script
# Run once on your Raspberry Pi to install dependencies

set -e

echo "=== piphone setup ==="

# 1. System dependencies
echo ""
echo "Installing baresip and audio tools..."
sudo apt-get update -qq
sudo apt-get install -y baresip baresip-core alsa-utils

# Install opus codec support (recommended for best audio quality)
sudo apt-get install -y libopus0 || echo "(opus not available — will use G.711)"

echo ""
echo "Checking baresip version..."
baresip -v 2>/dev/null || true

# 2. Python dependencies
echo ""
echo "Installing Python dependencies into venv..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

"$SCRIPT_DIR/.venv/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
echo "Python deps installed."

# 3. Create .env if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo ""
    echo "Created .env from template. Edit it now:"
    echo "  nano $SCRIPT_DIR/.env"
else
    echo ""
    echo ".env already exists — skipping."
fi

# 4. Audio check
echo ""
echo "Audio output devices (aplay -l):"
aplay -l 2>/dev/null || echo "(no audio devices found — connect a USB audio adapter)"

echo ""
echo "Audio input devices (arecord -l):"
arecord -l 2>/dev/null || echo "(no audio capture devices found)"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit your SIP credentials:  nano $SCRIPT_DIR/.env"
echo "  2. Run piphone:                $SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/piphone.py"
