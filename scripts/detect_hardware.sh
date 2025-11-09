#!/bin/bash

###############################################################################
# Hardware Detection Script for Pi Zero 2W
#
# Detects and reports hardware configuration including:
# - GT1151 touchscreen
# - PiSugar battery module
# - Available GPIO pins
# - I2C devices
#
# Usage: ./scripts/detect_hardware.sh [--json]
###############################################################################

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
OUTPUT_JSON=false
if [[ "$1" == "--json" ]]; then
    OUTPUT_JSON=true
fi

###############################################################################
# Run Python hardware detection
###############################################################################

if [ "$OUTPUT_JSON" = true ]; then
    # JSON output mode
    cd "$PROJECT_ROOT"
    python3 -c "
import json
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from shared.hardware_detect import get_hardware_info

info = get_hardware_info()
print(json.dumps(info, indent=2))
"
else
    # Human-readable output mode
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}Pi Zero 2W Hardware Detection${NC}                            ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Run detection
    cd "$PROJECT_ROOT"
    python3 "$PROJECT_ROOT/shared/hardware_detect.py"

    # Check I2C tools availability
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}SYSTEM INFORMATION${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

    # Check if i2c-tools is installed
    if command -v i2cdetect &> /dev/null; then
        echo -e "${GREEN}✓${NC} i2c-tools installed"
    else
        echo -e "${RED}✗${NC} i2c-tools NOT installed (install with: sudo apt-get install i2c-tools)"
    fi

    # Check if I2C is enabled
    if [ -e /dev/i2c-1 ]; then
        echo -e "${GREEN}✓${NC} I2C interface enabled (/dev/i2c-1)"
    else
        echo -e "${RED}✗${NC} I2C interface NOT enabled (enable with: sudo raspi-config)"
    fi

    # Check Python GPIO library
    if python3 -c "import RPi.GPIO" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} RPi.GPIO library available"
    else
        echo -e "${YELLOW}⚠${NC} RPi.GPIO library not installed (optional)"
    fi

    # Show environment variables
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo -e "  PIZERO_INPUT_MODE:        ${PIZERO_INPUT_MODE:-${YELLOW}not set${NC}}"
    echo -e "  PIZERO_HARDWARE_PROFILE:  ${PIZERO_HARDWARE_PROFILE:-${YELLOW}not set${NC}}"
    echo -e "  PIZERO_BUTTON_GPIO:       ${PIZERO_BUTTON_GPIO:-${YELLOW}not set${NC}}"

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Detection complete!${NC}"
    echo ""
    echo -e "To use JSON output: ${YELLOW}./scripts/detect_hardware.sh --json${NC}"
    echo ""
fi
