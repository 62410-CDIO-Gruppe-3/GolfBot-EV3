#!/bin/bash
# GolfBot-EV3 Automated Setup Script
# This script sets up the Python environment and dependencies for the GolfBot-EV3 project on your PC.

set -e

PROJECT_DIR="GolfBot-EV3"
# 2. Create a Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# 3. Activate the virtual environment
# shellcheck disable=SC1091
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Post-setup instructions
echo "\n--- SETUP COMPLETE ---"
echo "1. (Optional) Install Iriun Webcam on your PC and smartphone: https://iriun.com"
echo "2. (Manual) Set up your EV3 brick with MicroPython. See INSTALLATION_GUIDE.md for details."
echo "3. (Manual) Transfer project files to the EV3 brick as needed."
echo "4. (Manual) Configure API keys and network settings in the source files."
echo "5. To activate your environment in the future, run:"
echo "   source venv/bin/activate"
echo "6. To start the main application, run:"
echo "   python src/main.py"
echo "\nSee INSTALLATION_GUIDE.md for full instructions and troubleshooting." 