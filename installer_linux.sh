#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

install_tkinter_if_missing() {
    if python3 - <<'PY' >/dev/null 2>&1
import tkinter
PY
    then
        echo "tkinter is already available."
        return
    fi

    echo "tkinter was not found for python3."
    echo "Attempting to install the system package required by Tkinter..."

    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y python3-tk
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y python3-tkinter
    elif command -v zypper >/dev/null 2>&1; then
        sudo zypper install -y python3-tk
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -Sy --noconfirm tk
    else
        echo "Could not detect a supported package manager."
        echo "Please install tkinter for your distribution and run this script again."
        exit 1
    fi
}

echo "============================================"
echo "AnaTEMa Toolkit Linux Installer"
echo "============================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is not installed or not available in PATH."
    exit 1
fi

install_tkinter_if_missing

echo "Installing required Python packages..."
python3 -m pip install --upgrade pip
python3 -m pip install numpy scipy matplotlib requests beautifulsoup4 scikit-learn mplcursors plotly pandas openpyxl

echo "Installing local quadstarfiles package..."
pushd "$SCRIPT_DIR/quadstarfiles" >/dev/null
python3 -m pip install .
popd >/dev/null

echo
echo "Installation complete."
echo "You can now run AnaTEMa with: python3 main2_0.py"