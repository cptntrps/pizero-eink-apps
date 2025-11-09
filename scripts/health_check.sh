#!/bin/bash

################################################################################
# Pi Zero 2W Medicine Tracking System - Health Check Script
################################################################################
#
# Purpose: Comprehensive health check of application and system
# Usage:   ./health_check.sh [--format json|text] [--verbose]
# Author:  Claude Code Assistant
# Version: 1.0
#
################################################################################

set -o pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_FORMAT="text"
VERBOSE=false
LOG_FILE="${PROJECT_ROOT}/logs/health_check_$(date +%Y%m%d_%H%M%S).log"

# Application directories
APP_DIR="/home/pizero2w/pizero_apps"
BACKUP_DIR="${APP_DIR}/backups"
LOG_DIR="/var/log/pizero-app"

# Services to check
SERVICES=("pizero-webserver" "pizero-menu")

# Health check results
HEALTH_CHECKS=()
OVERALL_STATUS="HEALTHY"
FAILED_CHECKS=0
WARNING_CHECKS=0

# ============================================================================
# COLORS & FORMATTING
# ============================================================================

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

# Create log directory
create_log_directory() {
    local log_dir="${PROJECT_ROOT}/logs"
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir" 2>/dev/null || true
    fi
}

# Log function
log() {
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] ${message}" >> "$LOG_FILE" 2>/dev/null || true
}

# Add health check result
add_check() {
    local category=$1
    local name=$2
    local status=$3
    local message=$4
    local details=$5

    HEALTH_CHECKS+=("$category|$name|$status|$message|$details")

    case "$status" in
        FAIL)
            ((FAILED_CHECKS++))
            OVERALL_STATUS="UNHEALTHY"
            ;;
        WARN)
            ((WARNING_CHECKS++))
            if [[ "$OVERALL_STATUS" != "UNHEALTHY" ]]; then
                OVERALL_STATUS="WARNING"
            fi
            ;;
    esac
}

# Print header
print_header() {
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  Pi Zero 2W Medicine Tracking System - Health Check           ║"
    echo "║  Version 1.0 | Generated: $(date '+%Y-%m-%d %H:%M:%S')              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check service health
check_services() {
    local category="SERVICES"

    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            add_check "$category" "$service" "PASS" "Service is running" \
                "Active: $(systemctl is-active $service)"
        else
            add_check "$category" "$service" "FAIL" "Service not running" \
                "Status: $(systemctl is-active $service 2>/dev/null || echo 'unknown')"
        fi
    done
}

# Check application directory
check_app_directory() {
    local category="FILES"

    if [[ -d "$APP_DIR" ]]; then
        local size=$(du -sh "$APP_DIR" 2>/dev/null | awk '{print $1}')
        add_check "$category" "App Directory" "PASS" "Directory exists" "Path: $APP_DIR, Size: $size"
    else
        add_check "$category" "App Directory" "FAIL" "Directory not found" "Path: $APP_DIR"
    fi
}

# Check required files
check_required_files() {
    local category="FILES"
    local required_files=("medicine_app.py" "menu_button.py" "web_config.py" "config.json" "medicine_data.json")

    for file in "${required_files[@]}"; do
        if [[ -f "${APP_DIR}/${file}" ]]; then
            local size=$(ls -lh "${APP_DIR}/${file}" 2>/dev/null | awk '{print $5}')
            add_check "$category" "$file" "PASS" "File exists" "Size: $size"
        else
            add_check "$category" "$file" "FAIL" "File not found" "Expected: ${APP_DIR}/${file}"
        fi
    done
}

# Check configuration validity
check_configuration() {
    local category="CONFIG"

    if [[ -f "${APP_DIR}/config.json" ]]; then
        if python3 -c "import json; json.load(open('${APP_DIR}/config.json'))" 2>/dev/null; then
            add_check "$category" "config.json" "PASS" "Valid JSON" "Configuration is valid"
        else
            add_check "$category" "config.json" "FAIL" "Invalid JSON" "Configuration file is malformed"
        fi
    else
        add_check "$category" "config.json" "WARN" "File not found" "Configuration not present"
    fi

    if [[ -f "${APP_DIR}/medicine_data.json" ]]; then
        if python3 -c "import json; json.load(open('${APP_DIR}/medicine_data.json'))" 2>/dev/null; then
            add_check "$category" "medicine_data.json" "PASS" "Valid JSON" "Medicine data is valid"
        else
            add_check "$category" "medicine_data.json" "FAIL" "Invalid JSON" "Medicine data file is malformed"
        fi
    else
        add_check "$category" "medicine_data.json" "WARN" "File not found" "No medicine data file"
    fi
}

# Check file permissions
check_permissions() {
    local category="PERMISSIONS"

    if [[ -d "$APP_DIR" ]]; then
        local app_perms=$(stat -c %a "$APP_DIR" 2>/dev/null || echo "unknown")
        if [[ "$app_perms" == "755" ]]; then
            add_check "$category" "App Directory" "PASS" "Correct permissions" "Permissions: $app_perms"
        else
            add_check "$category" "App Directory" "WARN" "Non-standard permissions" "Permissions: $app_perms (expected 755)"
        fi
    fi
}

# Check disk space
check_disk_space() {
    local category="SYSTEM"

    local available=$(df /home 2>/dev/null | tail -1 | awk '{print $4}')
    local used=$(df /home 2>/dev/null | tail -1 | awk '{print $3}')
    local total=$(df /home 2>/dev/null | tail -1 | awk '{print $2}')
    local percent=$(df /home 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//')

    if (( percent > 90 )); then
        add_check "$category" "Disk Space" "FAIL" "Low disk space" \
            "Used: ${percent}% (${used}KB / ${total}KB)"
    elif (( percent > 80 )); then
        add_check "$category" "Disk Space" "WARN" "Disk space warning" \
            "Used: ${percent}% (${used}KB / ${total}KB)"
    else
        add_check "$category" "Disk Space" "PASS" "Sufficient disk space" \
            "Available: ${available}KB (${percent}% used)"
    fi
}

# Check system resources
check_system_resources() {
    local category="SYSTEM"

    # Check CPU
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    if (( ${cpu_usage%.*} > 80 )); then
        add_check "$category" "CPU Usage" "WARN" "High CPU usage" "CPU: ${cpu_usage}%"
    else
        add_check "$category" "CPU Usage" "PASS" "Normal CPU usage" "CPU: ${cpu_usage}%"
    fi

    # Check Memory
    local mem_usage=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100)}')
    if (( ${mem_usage%.*} > 80 )); then
        add_check "$category" "Memory Usage" "WARN" "High memory usage" "Memory: ${mem_usage}%"
    else
        add_check "$category" "Memory Usage" "PASS" "Normal memory usage" "Memory: ${mem_usage}%"
    fi
}

# Check network connectivity
check_network() {
    local category="NETWORK"

    if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
        add_check "$category" "Internet" "PASS" "Internet connectivity OK" "Ping to 8.8.8.8 successful"
    else
        add_check "$category" "Internet" "WARN" "No internet connectivity" "Cannot reach 8.8.8.8"
    fi

    # Check local network
    if ip addr show 2>/dev/null | grep -q "inet "; then
        local ip=$(hostname -I 2>/dev/null | awk '{print $1}')
        add_check "$category" "Local Network" "PASS" "Network interface active" "IP: $ip"
    else
        add_check "$category" "Local Network" "FAIL" "No network interfaces" "No active network interfaces"
    fi
}

# Check web server
check_web_server() {
    local category="SERVICES"

    if curl -s http://localhost:5000 >/dev/null 2>&1; then
        add_check "$category" "Web Server" "PASS" "Web server responding" "HTTP 200 from http://localhost:5000"
    else
        add_check "$category" "Web Server" "WARN" "Web server not responding" "Cannot reach http://localhost:5000"
    fi

    # Check if port is listening
    if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
        add_check "$category" "Port 5000" "PASS" "Port listening" "Port 5000 is bound"
    else
        add_check "$category" "Port 5000" "WARN" "Port not listening" "Port 5000 is not bound"
    fi
}

# Check logs
check_logs() {
    local category="LOGS"

    if [[ -d "$LOG_DIR" ]]; then
        local log_size=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')
        add_check "$category" "Log Directory" "PASS" "Log directory exists" "Path: $LOG_DIR, Size: $log_size"

        # Check for recent errors
        local error_count=$(grep -r "ERROR\|Exception\|Traceback" "$LOG_DIR" 2>/dev/null | wc -l)
        if (( error_count > 10 )); then
            add_check "$category" "Log Errors" "WARN" "Recent errors in logs" "Found $error_count error messages"
        else
            add_check "$category" "Log Errors" "PASS" "No critical errors in logs" "Error count: $error_count"
        fi
    else
        add_check "$category" "Log Directory" "WARN" "Log directory not found" "Path: $LOG_DIR"
    fi
}

# Check backups
check_backups() {
    local category="BACKUPS"

    if [[ -d "$BACKUP_DIR" ]]; then
        local backup_count=$(ls -d "${BACKUP_DIR}"/backup_* 2>/dev/null | wc -l)
        if (( backup_count > 0 )); then
            local latest=$(ls -d "${BACKUP_DIR}"/backup_* 2>/dev/null | sort -r | head -1)
            local latest_name=$(basename "$latest")
            add_check "$category" "Backups" "PASS" "$backup_count backups available" \
                "Latest: $latest_name"
        else
            add_check "$category" "Backups" "WARN" "No backups found" "Consider running deploy.sh"
        fi
    else
        add_check "$category" "Backups" "WARN" "Backup directory not found" "Path: $BACKUP_DIR"
    fi
}

# Check systemd services
check_systemd() {
    local category="SYSTEMD"

    for service in "${SERVICES[@]}"; do
        if systemctl is-enabled --quiet "$service" 2>/dev/null; then
            add_check "$category" "$service" "PASS" "Service enabled at boot" "Enabled: yes"
        else
            add_check "$category" "$service" "WARN" "Service not enabled" "Service will not start at boot"
        fi
    done
}

# Print text output
print_text_output() {
    echo ""
    echo -e "${CYAN}━━━ DETAILED RESULTS ━━━${NC}"
    echo ""

    local current_category=""
    for check in "${HEALTH_CHECKS[@]}"; do
        IFS='|' read -r category name status message details <<< "$check"

        if [[ "$category" != "$current_category" ]]; then
            current_category="$category"
            echo ""
            echo -e "${BLUE}${current_category}${NC}"
            echo "─────────────────────────────────────────────────────────────"
        fi

        case "$status" in
            PASS) echo -e "  ${GREEN}✓${NC} $name: $message" ;;
            WARN) echo -e "  ${YELLOW}⚠${NC} $name: $message" ;;
            FAIL) echo -e "  ${RED}✗${NC} $name: $message" ;;
        esac

        if [[ "$VERBOSE" == true && -n "$details" ]]; then
            echo "     $details"
        fi
    done

    echo ""
}

# Print json output
print_json_output() {
    echo "{"
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"overall_status\": \"$OVERALL_STATUS\","
    echo "  \"summary\": {"
    echo "    \"total_checks\": ${#HEALTH_CHECKS[@]},"
    echo "    \"passed\": $((${#HEALTH_CHECKS[@]} - FAILED_CHECKS - WARNING_CHECKS)),"
    echo "    \"warnings\": $WARNING_CHECKS,"
    echo "    \"failed\": $FAILED_CHECKS"
    echo "  },"
    echo "  \"checks\": ["

    local first=true
    for check in "${HEALTH_CHECKS[@]}"; do
        IFS='|' read -r category name status message details <<< "$check"

        if [[ "$first" == false ]]; then
            echo ","
        fi
        first=false

        echo -n "    {"
        echo -n "\"category\": \"$category\", "
        echo -n "\"name\": \"$name\", "
        echo -n "\"status\": \"$status\", "
        echo -n "\"message\": \"$message\""
        if [[ -n "$details" ]]; then
            echo -n ", \"details\": \"$details\""
        fi
        echo -n "}"
    done

    echo ""
    echo "  ]"
    echo "}"
}

# Print summary
print_summary() {
    echo ""
    if [[ "$OUTPUT_FORMAT" == "json" ]]; then
        print_json_output
    else
        echo -e "${CYAN}━━━ HEALTH CHECK SUMMARY ━━━${NC}"
        echo ""
        case "$OVERALL_STATUS" in
            HEALTHY)  echo -e "Overall Status: ${GREEN}HEALTHY${NC}" ;;
            WARNING)  echo -e "Overall Status: ${YELLOW}WARNING${NC}" ;;
            UNHEALTHY) echo -e "Overall Status: ${RED}UNHEALTHY${NC}" ;;
        esac

        echo ""
        echo "Checks Performed: ${#HEALTH_CHECKS[@]}"
        echo -e "  ${GREEN}Passed:${NC} $((${#HEALTH_CHECKS[@]} - FAILED_CHECKS - WARNING_CHECKS))"
        echo -e "  ${YELLOW}Warnings:${NC} $WARNING_CHECKS"
        echo -e "  ${RED}Failed:${NC} $FAILED_CHECKS"
        echo ""
        echo "Log file: $LOG_FILE"
    fi
}

# Main execution
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --format)
                OUTPUT_FORMAT=$2
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                print_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # Setup
    create_log_directory

    if [[ "$OUTPUT_FORMAT" != "json" ]]; then
        print_header
    fi

    # Run checks
    check_services
    check_app_directory
    check_required_files
    check_configuration
    check_permissions
    check_disk_space
    check_system_resources
    check_network
    check_web_server
    check_logs
    check_backups
    check_systemd

    # Print results
    if [[ "$OUTPUT_FORMAT" != "json" ]]; then
        print_text_output
    fi
    print_summary

    # Log results
    log "Health check completed. Overall status: $OVERALL_STATUS"

    # Exit code based on overall status
    case "$OVERALL_STATUS" in
        HEALTHY)  exit 0 ;;
        WARNING)  exit 1 ;;
        UNHEALTHY) exit 2 ;;
    esac
}

# Help text
print_usage() {
    cat << EOF

Usage: $0 [OPTIONS]

Options:
    --format json|text      Output format (default: text)
    --verbose               Show detailed information
    --help                  Show this help message

Description:
    Performs comprehensive health checks on the Pi Zero 2W Medicine Tracking
    System, including services, files, configuration, system resources, and
    network connectivity.

Examples:
    ./$0                        # Run health check (text output)
    ./$0 --format json          # Output as JSON
    ./$0 --verbose              # Detailed output
    ./$0 --format json --verbose # JSON with details

Exit Codes:
    0 = HEALTHY
    1 = WARNING
    2 = UNHEALTHY

Log file: ${LOG_FILE}

EOF
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
