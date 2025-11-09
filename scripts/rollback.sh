#!/bin/bash

################################################################################
# Pi Zero 2W Medicine Tracking System - Rollback Script
################################################################################
#
# Purpose: Rollback to a previous deployment version
# Usage:   ./rollback.sh [--backup-id TIMESTAMP] [--dry-run]
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
DRY_RUN=false
VERBOSE=true
LOG_FILE="${PROJECT_ROOT}/logs/rollback_$(date +%Y%m%d_%H%M%S).log"

# Application directories
APP_DIR="/home/pizero2w/pizero_apps"
BACKUP_DIR="${APP_DIR}/backups"
TARGET_BACKUP=""

# Services to manage
SERVICES=("pizero-webserver" "pizero-menu")

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

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[${timestamp}] [${level}] ${message}" >> "$LOG_FILE" 2>/dev/null || true

    if [[ "$VERBOSE" == true ]]; then
        case "$level" in
            ERROR)   echo -e "${RED}[✗ ERROR]${NC} ${message}" >&2 ;;
            WARN)    echo -e "${YELLOW}[⚠ WARN]${NC} ${message}" ;;
            INFO)    echo -e "${BLUE}[ℹ INFO]${NC} ${message}" ;;
            SUCCESS) echo -e "${GREEN}[✓ OK]${NC} ${message}" ;;
            ACTION)  echo -e "${CYAN}[→]${NC} ${message}" ;;
            *)       echo "${message}" ;;
        esac
    fi
}

# Print header
print_header() {
    clear
    echo -e "${MAGENTA}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  Pi Zero 2W Medicine Tracking System - Rollback Script        ║"
    echo "║  Version 1.0                                                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print section header
section_header() {
    echo ""
    echo -e "${CYAN}━━━ $1 ━━━${NC}"
}

# List available backups
list_backups() {
    section_header "Available Backups"

    if [[ ! -d "$BACKUP_DIR" ]]; then
        log ERROR "Backup directory not found: $BACKUP_DIR"
        return 1
    fi

    local backups=($(ls -d "${BACKUP_DIR}"/backup_* 2>/dev/null | sort -r))

    if [[ ${#backups[@]} -eq 0 ]]; then
        log WARN "No backups found in: $BACKUP_DIR"
        return 1
    fi

    echo ""
    printf "%-25s %-30s %-15s\n" "ID (Timestamp)" "Path" "Size"
    echo "─────────────────────────────────────────────────────────────────"

    local idx=0
    for backup in "${backups[@]}"; do
        local backup_name=$(basename "$backup")
        local backup_size=$(du -sh "$backup" 2>/dev/null | awk '{print $1}')
        printf "%-25s %-30s %-15s\n" "$backup_name" "$(basename $backup)" "$backup_size"

        if [[ $idx -eq 0 ]]; then
            echo "  ^ Most recent backup (recommended)"
        fi
        ((idx++))
    done

    echo ""
    return 0
}

# Validate backup
validate_backup() {
    local backup_path=$1

    section_header "Validating Backup"

    if [[ ! -d "$backup_path" ]]; then
        log ERROR "Backup directory not found: $backup_path"
        return 1
    fi

    if [[ ! -f "${backup_path}/BACKUP_INFO.txt" ]]; then
        log WARN "BACKUP_INFO.txt not found (old backup format)"
    else
        log SUCCESS "Backup info found"
        echo ""
        cat "${backup_path}/BACKUP_INFO.txt" | sed 's/^/  /'
        echo ""
    fi

    # Check for critical files
    local critical_files=("medicine_app.py" "menu_button.py" "web_config.py")
    local missing_files=false

    for file in "${critical_files[@]}"; do
        if [[ -f "${backup_path}/${file}" ]]; then
            log INFO "✓ $file"
        else
            log WARN "✗ $file (not found)"
            missing_files=true
        fi
    done

    if [[ "$missing_files" == true ]]; then
        log WARN "Some files are missing from backup"
        return 1
    fi

    log SUCCESS "Backup validation passed"
    return 0
}

# Confirm action
confirm_rollback() {
    local backup_path=$1
    local backup_name=$(basename "$backup_path")

    echo ""
    echo -e "${YELLOW}⚠ CONFIRMATION REQUIRED ⚠${NC}"
    echo ""
    echo "This will rollback to:"
    echo "  Backup ID: $backup_name"
    echo "  Location: $backup_path"
    echo ""
    echo "Actions that will be performed:"
    echo "  1. Stop all services"
    echo "  2. Restore files from backup"
    echo "  3. Restart services"
    echo ""

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "DRY-RUN mode - no changes will be made"
        echo ""
        read -p "Proceed with DRY-RUN? (yes/no): " response
    else
        read -p "Proceed with ROLLBACK? (yes/no): " response
    fi

    if [[ "$response" != "yes" && "$response" != "y" ]]; then
        log INFO "Rollback cancelled by user"
        return 1
    fi

    return 0
}

# Stop services
stop_services() {
    section_header "Stopping Services"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would stop services:"
        for service in "${SERVICES[@]}"; do
            log INFO "  - $service"
        done
        return 0
    fi

    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log ACTION "Stopping $service..."
            if systemctl stop "$service" >/dev/null 2>&1; then
                log SUCCESS "Stopped: $service"
            else
                log WARN "Failed to stop: $service"
            fi
        else
            log INFO "Service not running: $service"
        fi
    done

    sleep 2
    return 0
}

# Restore from backup
restore_backup() {
    local backup_path=$1
    section_header "Restoring Files"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would restore from: $backup_path"
        return 0
    fi

    # Create current working backup (for emergency rollback)
    local emergency_backup="${BACKUP_DIR}/emergency_${RANDOM}"
    mkdir -p "$emergency_backup" 2>/dev/null || true

    # Backup current files before restore
    log ACTION "Creating emergency backup of current files..."
    if cp "${APP_DIR}"/*.py "${emergency_backup}/" 2>/dev/null; then
        log INFO "Current files backed up to: $emergency_backup"
    fi

    # Restore files
    log ACTION "Restoring files from backup..."

    # Copy Python files
    local python_files=("medicine_app.py" "menu_button.py" "web_config.py" "config.json")
    for file in "${python_files[@]}"; do
        if [[ -f "${backup_path}/${file}" ]]; then
            if cp "${backup_path}/${file}" "${APP_DIR}/" 2>/dev/null; then
                log SUCCESS "Restored: $file"
            else
                log ERROR "Failed to restore: $file"
                return 1
            fi
        fi
    done

    # Restore display library
    if [[ -d "${backup_path}/display" ]]; then
        log ACTION "Restoring display library..."
        if cp -r "${backup_path}/display" "${APP_DIR}/" 2>/dev/null; then
            log SUCCESS "Restored: display library"
        else
            log ERROR "Failed to restore display library"
            return 1
        fi
    fi

    log SUCCESS "Files restored successfully"
    return 0
}

# Start services
start_services() {
    section_header "Starting Services"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would start services:"
        for service in "${SERVICES[@]}"; do
            log INFO "  - $service"
        done
        return 0
    fi

    for service in "${SERVICES[@]}"; do
        log ACTION "Starting $service..."
        if systemctl start "$service" >/dev/null 2>&1; then
            log SUCCESS "Started: $service"
        else
            log ERROR "Failed to start: $service"
            return 1
        fi
    done

    sleep 3
    return 0
}

# Verify rollback
verify_rollback() {
    section_header "Verifying Rollback"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Verification skipped"
        return 0
    fi

    # Check services
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log SUCCESS "Service healthy: $service"
        else
            log WARN "Service not running: $service"
        fi
    done

    return 0
}

# Print summary
print_summary() {
    local backup_name=$(basename "$TARGET_BACKUP")

    section_header "Rollback Summary"

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}DRY-RUN Completed${NC}"
        echo ""
        echo "Would have rolled back to:"
        echo "  Backup ID: $backup_name"
        echo "  Location: $TARGET_BACKUP"
    else
        echo -e "${GREEN}Rollback Complete!${NC}"
        echo ""
        echo "Rolled back to:"
        echo "  Backup ID: $backup_name"
        echo "  Location: $TARGET_BACKUP"
        echo ""
        echo "Service Status:"
        for service in "${SERVICES[@]}"; do
            if systemctl is-active --quiet "$service" 2>/dev/null; then
                echo "  ✓ $service is running"
            else
                echo "  ✗ $service is NOT running"
            fi
        done
    fi

    echo ""
    echo "Next Steps:"
    echo "  1. Verify application functionality"
    echo "  2. Check logs: tail -f /var/log/pizero-app/webserver.log"
    echo "  3. Investigate what caused the deployment failure"
    echo ""
    echo "Log file: $LOG_FILE"
}

# Print error summary
print_error_summary() {
    section_header "Rollback Failed"

    echo -e "${RED}Rollback encountered errors!${NC}"
    echo ""
    echo "Your system may be in an inconsistent state."
    echo ""
    echo "Actions to take:"
    echo "  1. Review the log file:"
    echo "     cat $LOG_FILE"
    echo "  2. Check service status:"
    echo "     systemctl status pizero-webserver"
    echo "     systemctl status pizero-menu"
    echo "  3. Manually restore files from backup:"
    echo "     cp ${TARGET_BACKUP}/* ${APP_DIR}/"
    echo "  4. Restart services:"
    echo "     sudo systemctl restart pizero-webserver pizero-menu"
}

# Main execution
main() {
    local rollback_failed=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup-id)
                TARGET_BACKUP="${BACKUP_DIR}/backup_${2}"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
            --quiet)
                VERBOSE=false
                ;;
            --help)
                print_usage
                exit 0
                ;;
            *)
                log ERROR "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # Setup
    create_log_directory
    print_header

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}DRY-RUN MODE ENABLED${NC} - No changes will be made"
        echo ""
    fi

    # If no backup specified, use most recent
    if [[ -z "$TARGET_BACKUP" ]]; then
        list_backups || exit 1

        # Get most recent backup
        local most_recent=$(ls -d "${BACKUP_DIR}"/backup_* 2>/dev/null | sort -r | head -1)
        if [[ -z "$most_recent" ]]; then
            log ERROR "No backups found"
            exit 1
        fi

        TARGET_BACKUP="$most_recent"
        echo ""
        log INFO "Using most recent backup: $(basename $TARGET_BACKUP)"
    fi

    # Execution
    validate_backup "$TARGET_BACKUP" || exit 1
    confirm_rollback "$TARGET_BACKUP" || exit 1
    stop_services || rollback_failed=true
    restore_backup "$TARGET_BACKUP" || rollback_failed=true
    start_services || rollback_failed=true
    verify_rollback || rollback_failed=true

    # Summary
    if [[ "$rollback_failed" == true ]]; then
        print_error_summary
        exit 1
    else
        print_summary
        exit 0
    fi
}

# Help text
print_usage() {
    cat << EOF

Usage: $0 [OPTIONS]

Options:
    --backup-id TIMESTAMP   Rollback to specific backup (use timestamp format: YYYYMMdd_HHMMSS)
    --dry-run               Run without making any changes
    --quiet                 Suppress output (log only)
    --help                  Show this help message

Description:
    Rolls back to a previous deployment backup. If no backup ID is specified,
    uses the most recent backup. Lists all available backups for reference.

Examples:
    ./$0                                    # Rollback to most recent
    ./$0 --dry-run                          # Preview rollback
    ./$0 --backup-id 20251108_143022        # Rollback to specific backup

Log file: ${LOG_FILE}

EOF
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
