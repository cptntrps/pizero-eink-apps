#!/bin/bash

################################################################################
# Pi Zero 2W Medicine Tracking System - Monitoring Script
################################################################################
#
# Purpose: Continuous monitoring of application and system metrics
# Usage:   ./monitor.sh [--interval SECONDS] [--duration MINUTES] [--log-file PATH]
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
INTERVAL=5
DURATION=0  # 0 = infinite
LOG_FILE=""
ENABLE_LOGGING=false
VERBOSE=true

# Application directories
APP_DIR="/home/pizero2w/pizero_apps"
LOG_DIR="/var/log/pizero-app"

# Services to monitor
SERVICES=("pizero-webserver" "pizero-menu")

# Thresholds
CPU_THRESHOLD=80
MEM_THRESHOLD=80
DISK_THRESHOLD=80

# ============================================================================
# COLORS & FORMATTING
# ============================================================================

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

# Format timestamp
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Log message
log_message() {
    local message="$1"
    local timestamp=$(get_timestamp)

    if [[ "$VERBOSE" == true ]]; then
        echo -e "${CYAN}[${timestamp}]${NC} ${message}"
    fi

    if [[ "$ENABLE_LOGGING" == true && -n "$LOG_FILE" ]]; then
        echo "[${timestamp}] ${message}" >> "$LOG_FILE"
    fi
}

# Print header
print_header() {
    clear
    echo -e "${BLUE}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  Pi Zero 2W Medicine Tracking System - Monitoring              ║"
    echo "║  Version 1.0                                                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "Interval: ${INTERVAL}s | Duration: $([[ $DURATION -gt 0 ]] && echo "${DURATION}min" || echo "∞")"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
}

# Get service status
get_service_status() {
    local service=$1
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo -e "${GREEN}●${NC} Running"
    else
        echo -e "${RED}●${NC} Stopped"
    fi
}

# Get service uptime
get_service_uptime() {
    local service=$1
    local active_time=$(systemctl show -p ActiveEnterTimestamp "$service" 2>/dev/null | cut -d'=' -f2)

    if [[ -z "$active_time" ]]; then
        echo "unknown"
        return
    fi

    local start_epoch=$(date -d "$active_time" +%s 2>/dev/null)
    local now_epoch=$(date +%s)
    local uptime_seconds=$((now_epoch - start_epoch))

    if (( uptime_seconds < 0 )); then
        echo "not running"
        return
    fi

    local days=$((uptime_seconds / 86400))
    local hours=$(( (uptime_seconds % 86400) / 3600 ))
    local minutes=$(( (uptime_seconds % 3600) / 60 ))

    if (( days > 0 )); then
        printf "%dd %dh %dm" "$days" "$hours" "$minutes"
    elif (( hours > 0 )); then
        printf "%dh %dm" "$hours" "$minutes"
    else
        printf "%dm" "$minutes"
    fi
}

# Get CPU usage
get_cpu_usage() {
    local cpu_usage=$(top -bn1 2>/dev/null | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{printf("%.1f", 100 - $1)}')
    echo "${cpu_usage}%"
}

# Get memory usage
get_memory_usage() {
    local mem_info=$(free -b 2>/dev/null | grep Mem)
    local total=$(echo "$mem_info" | awk '{print $2}')
    local used=$(echo "$mem_info" | awk '{print $3}')
    local percent=$(awk "BEGIN {printf(\"%.1f\", ($used/$total)*100)}")
    echo "${percent}%"
}

# Get disk usage
get_disk_usage() {
    local disk_usage=$(df /home 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//')
    echo "${disk_usage}%"
}

# Get process count
get_process_count() {
    ps aux | wc -l
}

# Get network stats
get_network_stats() {
    local rx_bytes=$(cat /proc/net/dev 2>/dev/null | grep wlan0 | awk '{print $2}')
    local tx_bytes=$(cat /proc/net/dev 2>/dev/null | grep wlan0 | awk '{print $10}')

    if [[ -z "$rx_bytes" ]]; then
        echo "N/A"
        return
    fi

    local rx_mb=$(awk "BEGIN {printf(\"%.2f\", $rx_bytes/1024/1024)}")
    local tx_mb=$(awk "BEGIN {printf(\"%.2f\", $tx_bytes/1024/1024)}")

    echo "RX: ${rx_mb}MB | TX: ${tx_mb}MB"
}

# Check application files
check_app_files() {
    local missing=0
    local required_files=("medicine_app.py" "menu_button.py" "web_config.py" "config.json")

    for file in "${required_files[@]}"; do
        if [[ ! -f "${APP_DIR}/${file}" ]]; then
            ((missing++))
        fi
    done

    echo "$missing"
}

# Get application file count
get_file_count() {
    local count=$(ls -1 "${APP_DIR}"/*.py 2>/dev/null | wc -l)
    echo "$count"
}

# Get log file size
get_log_size() {
    if [[ -d "$LOG_DIR" ]]; then
        du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}'
    else
        echo "N/A"
    fi
}

# Check recent errors
check_recent_errors() {
    local error_count=0

    if [[ -d "$LOG_DIR" ]]; then
        error_count=$(grep -r "ERROR\|Exception" "$LOG_DIR" 2>/dev/null | tail -100 | wc -l)
    fi

    echo "$error_count"
}

# Print service metrics
print_service_metrics() {
    echo ""
    echo -e "${CYAN}━━━ SERVICES ━━━${NC}"

    for service in "${SERVICES[@]}"; do
        local status=$(get_service_status "$service")
        local uptime=$(get_service_uptime "$service")
        printf "%-25s %s (uptime: %s)\n" "$service" "$status" "$uptime"
    done
}

# Print system metrics
print_system_metrics() {
    echo ""
    echo -e "${CYAN}━━━ SYSTEM RESOURCES ━━━${NC}"

    local cpu=$(get_cpu_usage)
    local mem=$(get_memory_usage)
    local disk=$(get_disk_usage)

    # Color coding for thresholds
    if (( ${cpu%.*} > CPU_THRESHOLD )); then
        cpu_color="${RED}${cpu}${NC}"
    else
        cpu_color="${GREEN}${cpu}${NC}"
    fi

    if (( ${mem%.*} > MEM_THRESHOLD )); then
        mem_color="${RED}${mem}${NC}"
    else
        mem_color="${GREEN}${mem}${NC}"
    fi

    if (( ${disk%.*} > DISK_THRESHOLD )); then
        disk_color="${RED}${disk}${NC}"
    else
        disk_color="${GREEN}${disk}${NC}"
    fi

    printf "CPU Usage:       %-10s Memory Usage:    %-10s Disk Usage:      %-10s\n" \
        -e "$cpu_color" -e "$mem_color" -e "$disk_color"
    printf "Processes:       %-10s Network (wlan0): %s\n" \
        "$(get_process_count)" "$(get_network_stats)"
}

# Print application metrics
print_application_metrics() {
    echo ""
    echo -e "${CYAN}━━━ APPLICATION ━━━${NC}"

    local missing_files=$(check_app_files)
    local file_count=$(get_file_count)
    local log_size=$(get_log_size)
    local recent_errors=$(check_recent_errors)

    if (( missing_files > 0 )); then
        missing_color="${RED}${missing_files}${NC}"
    else
        missing_color="${GREEN}0${NC}"
    fi

    if (( recent_errors > 0 )); then
        error_color="${RED}${recent_errors}${NC}"
    else
        error_color="${GREEN}0${NC}"
    fi

    printf "App Directory:   %-10s Missing Files:   %-10s Log Size:        %s\n" \
        "$APP_DIR" -e "$missing_color" "$log_size"
    printf "Python Files:    %-10s Recent Errors:   %s\n" \
        "$file_count" -e "$error_color"
}

# Print web server metrics
print_web_metrics() {
    echo ""
    echo -e "${CYAN}━━━ WEB SERVER ━━━${NC}"

    if curl -s http://localhost:5000 >/dev/null 2>&1; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000)
        printf "Web Server:      ${GREEN}Responding${NC} (HTTP %s)\n" "$response"
    else
        printf "Web Server:      ${RED}Not Responding${NC}\n"
    fi

    # Get connection count
    local connections=$(netstat -an 2>/dev/null | grep -c :5000 || echo "0")
    printf "Connections:     %-10s\n" "$connections"
}

# Print footer
print_footer() {
    echo ""
    echo -e "${CYAN}━━━ MONITORING ━━━${NC}"
    local now=$(get_timestamp)
    printf "Last Update:     %s\n" "$now"
}

# Display monitoring screen
display_monitor() {
    print_service_metrics
    print_system_metrics
    print_application_metrics
    print_web_metrics
    print_footer
}

# Start continuous monitoring
start_monitoring() {
    local elapsed=0
    local max_seconds=$((DURATION * 60))

    print_header
    log_message "Monitoring started (interval: ${INTERVAL}s)"

    while true; do
        display_monitor

        # Check if duration limit exceeded
        if [[ $DURATION -gt 0 && $elapsed -ge $max_seconds ]]; then
            log_message "Monitoring duration limit reached"
            break
        fi

        sleep "$INTERVAL"
        ((elapsed += INTERVAL))

        # Clear screen for next update (except last iteration)
        if [[ $DURATION -eq 0 ]] || [[ $elapsed -lt $max_seconds ]]; then
            clear
            print_header
        fi
    done

    log_message "Monitoring stopped"
}

# Trap Ctrl+C
cleanup() {
    echo ""
    log_message "Monitoring interrupted by user"
    exit 0
}

# Main execution
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --interval)
                INTERVAL=$2
                shift 2
                ;;
            --duration)
                DURATION=$2
                shift 2
                ;;
            --log-file)
                LOG_FILE=$2
                ENABLE_LOGGING=true
                shift 2
                ;;
            --quiet)
                VERBOSE=false
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

    # Validate arguments
    if ! [[ "$INTERVAL" =~ ^[0-9]+$ ]] || (( INTERVAL < 1 )); then
        echo "Error: --interval must be a positive integer"
        exit 1
    fi

    if ! [[ "$DURATION" =~ ^[0-9]+$ ]]; then
        echo "Error: --duration must be a non-negative integer"
        exit 1
    fi

    # Setup
    trap cleanup SIGINT SIGTERM

    if [[ "$ENABLE_LOGGING" == true && ! -d "$(dirname "$LOG_FILE")" ]]; then
        mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true
    fi

    # Start monitoring
    start_monitoring
}

# Help text
print_usage() {
    cat << EOF

Usage: $0 [OPTIONS]

Options:
    --interval SECONDS      Update interval in seconds (default: 5)
    --duration MINUTES      Run for specified minutes (default: 0 = infinite)
    --log-file PATH         Save monitoring logs to file
    --quiet                 Suppress screen output
    --help                  Show this help message

Description:
    Continuously monitors the Pi Zero 2W Medicine Tracking System,
    displaying real-time metrics for services, system resources,
    application status, and web server connectivity.

Examples:
    ./$0                              # Monitor with 5s interval
    ./$0 --interval 10                # Monitor with 10s interval
    ./$0 --duration 30                # Monitor for 30 minutes
    ./$0 --log-file /tmp/monitor.log  # Log output to file
    ./$0 --interval 5 --duration 60   # Monitor for 60 min with 5s updates

Thresholds:
    CPU: > ${CPU_THRESHOLD}% = warning
    Memory: > ${MEM_THRESHOLD}% = warning
    Disk: > ${DISK_THRESHOLD}% = warning

Press Ctrl+C to stop monitoring

EOF
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
