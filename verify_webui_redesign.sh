#!/bin/bash
# Verification Script for WebUI Backend Redesign
# Phase 4 - Agent 4.1

echo "========================================="
echo "WebUI Backend Redesign Verification"
echo "Phase 4 - Agent 4.1"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Verify web_config.py structure
echo "1. Checking web_config.py structure..."
if grep -q "def proxy_api" /home/user/pizerowgpio/web_config.py; then
    echo -e "${GREEN}✓${NC} Proxy endpoint found"
else
    echo -e "${RED}✗${NC} Proxy endpoint NOT found"
fi

if grep -q "MAIN_API_URL" /home/user/pizerowgpio/web_config.py; then
    echo -e "${GREEN}✓${NC} Main API URL configured"
else
    echo -e "${RED}✗${NC} Main API URL NOT configured"
fi

if grep -q "MEDICINE_DATA_FILE" /home/user/pizerowgpio/web_config.py; then
    echo -e "${RED}✗${NC} MEDICINE_DATA_FILE reference still exists (should be removed)"
else
    echo -e "${GREEN}✓${NC} MEDICINE_DATA_FILE removed"
fi

if grep -q "flask_cors" /home/user/pizerowgpio/web_config.py; then
    echo -e "${GREEN}✓${NC} CORS support added"
else
    echo -e "${RED}✗${NC} CORS support NOT added"
fi

echo ""

# Check 2: Verify medicine endpoints removed
echo "2. Checking medicine endpoints removed..."
MEDICINE_ROUTES=$(grep -c "/api/medicine/" /home/user/pizerowgpio/web_config.py 2>/dev/null || echo "0")
if [ "$MEDICINE_ROUTES" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All medicine endpoints removed ($MEDICINE_ROUTES found)"
else
    echo -e "${RED}✗${NC} Medicine endpoints still exist ($MEDICINE_ROUTES found)"
fi

echo ""

# Check 3: Verify config routes updated
echo "3. Checking config routes..."
if grep -q "VALID_CONFIG_SECTIONS" /home/user/pizerowgpio/web_config.py; then
    echo -e "${GREEN}✓${NC} Valid config sections defined"

    # Check if deleted apps are excluded
    if grep "VALID_CONFIG_SECTIONS" /home/user/pizerowgpio/web_config.py | grep -q "weather\|mbta\|pomodoro"; then
        echo -e "${RED}✗${NC} Deleted apps still in VALID_CONFIG_SECTIONS"
    else
        echo -e "${GREEN}✓${NC} Deleted apps removed from VALID_CONFIG_SECTIONS"
    fi
else
    echo -e "${RED}✗${NC} VALID_CONFIG_SECTIONS NOT defined"
fi

echo ""

# Check 4: Verify API config routes updated
echo "4. Checking main API config routes..."
if grep -q "# Valid configuration sections (REMOVED: weather, mbta, pomodoro" /home/user/pizerowgpio/api/v1/routes/config.py; then
    echo -e "${GREEN}✓${NC} API config routes updated with removal comment"
else
    echo -e "${YELLOW}⚠${NC} API config routes may not have removal comment"
fi

WEATHER_ROUTE=$(grep -c "def weather_config" /home/user/pizerowgpio/api/v1/routes/config.py 2>/dev/null || echo "0")
MBTA_ROUTE=$(grep -c "def mbta_config" /home/user/pizerowgpio/api/v1/routes/config.py 2>/dev/null || echo "0")
POMODORO_ROUTE=$(grep -c "def pomodoro_config" /home/user/pizerowgpio/api/v1/routes/config.py 2>/dev/null || echo "0")

if [ "$WEATHER_ROUTE" -eq 0 ] && [ "$MBTA_ROUTE" -eq 0 ] && [ "$POMODORO_ROUTE" -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Deleted app endpoints removed from config.py"
else
    echo -e "${RED}✗${NC} Deleted app endpoints still exist (weather: $WEATHER_ROUTE, mbta: $MBTA_ROUTE, pomodoro: $POMODORO_ROUTE)"
fi

echo ""

# Check 5: Verify requirements.txt updated
echo "5. Checking requirements.txt..."
if grep -q "requests>=" /home/user/pizerowgpio/requirements.txt; then
    echo -e "${GREEN}✓${NC} requests library added"
else
    echo -e "${RED}✗${NC} requests library NOT added"
fi

if grep -q "Flask-CORS>=" /home/user/pizerowgpio/requirements.txt; then
    echo -e "${GREEN}✓${NC} Flask-CORS present"
else
    echo -e "${RED}✗${NC} Flask-CORS NOT present"
fi

echo ""

# Check 6: Count endpoints
echo "6. Endpoint statistics..."
WEBUI_ROUTES=$(grep -c "^@app.route" /home/user/pizerowgpio/web_config.py)
API_MEDICINE_ROUTES=$(grep -c "^@api_v1_bp.route" /home/user/pizerowgpio/api/v1/routes/medicines.py)
API_TRACKING_ROUTES=$(grep -c "^@api_v1_bp.route" /home/user/pizerowgpio/api/v1/routes/tracking.py)
API_CONFIG_ROUTES=$(grep -c "^@api_v1_bp.route" /home/user/pizerowgpio/api/v1/routes/config.py)

echo -e "   WebUI endpoints:     ${GREEN}$WEBUI_ROUTES${NC} (expected: ~6)"
echo -e "   API medicine routes: ${GREEN}$API_MEDICINE_ROUTES${NC} (expected: ~10)"
echo -e "   API tracking routes: ${GREEN}$API_TRACKING_ROUTES${NC} (expected: ~9)"
echo -e "   API config routes:   ${GREEN}$API_CONFIG_ROUTES${NC} (expected: ~12)"

echo ""

# Check 7: File sizes
echo "7. Code metrics..."
WEBUI_LINES=$(wc -l < /home/user/pizerowgpio/web_config.py)
echo -e "   web_config.py:       ${GREEN}$WEBUI_LINES lines${NC} (expected: ~306)"

echo ""

# Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo ""
echo "Expected changes:"
echo "  ✓ Proxy endpoint added to web_config.py"
echo "  ✓ 6 medicine endpoints removed from web_config.py"
echo "  ✓ MEDICINE_DATA_FILE reference removed"
echo "  ✓ CORS support added"
echo "  ✓ VALID_CONFIG_SECTIONS excludes deleted apps"
echo "  ✓ API config routes exclude weather, mbta, pomodoro"
echo "  ✓ requests library added to requirements.txt"
echo ""
echo "Run 'cat PHASE4_AGENT4.1_REPORT.md' for detailed report"
echo ""
