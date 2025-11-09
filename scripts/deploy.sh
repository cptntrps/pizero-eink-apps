#!/bin/bash

################################################################################
# Pi Zero 2W Medicine Tracking System - Deployment Script
################################################################################
#
# Purpose: Deploy/update application with automatic backup and rollback capability
# Usage:   ./deploy.sh [--dry-run] [--no-backup] [--force]
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
NO_BACKUP=false
FORCE=false
VERBOSE=true
SKIP_HEALTH_CHECK=false
LOG_FILE="${PROJECT_ROOT}/logs/deploy_$(date +%Y%m%d_%H%M%S).log"

# Application directories
APP_DIR="/home/pizero2w/pizero_apps"
BACKUP_DIR="${APP_DIR}/backups"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_BACKUP="${BACKUP_DIR}/backup_${BACKUP_TIMESTAMP}"

# Services to manage
SERVICES=("pizero-webserver" "pizero-menu")

# Files to deploy
DEPLOY_FILES=(
    "medicine_app.py"
    "menu_button.py"
    "web_config.py"
    "config.json"
)

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
    echo "║  Pi Zero 2W Medicine Tracking System - Deployment Script      ║"
    echo "║  Version 1.0                                                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print section header
section_header() {
    echo ""
    echo -e "${CYAN}━━━ $1 ━━━${NC}"
}

# Verify application directory exists
verify_app_directory() {
    section_header "Verifying Application Directory"

    if [[ ! -d "$APP_DIR" ]]; then
        log ERROR "Application directory not found: $APP_DIR"
        log INFO "Run install.sh first to set up the application"
        return 1
    fi

    log SUCCESS "Application directory verified: $APP_DIR"
    return 0
}

# Create backup
create_backup() {
    section_header "Creating Backup"

    if [[ "$NO_BACKUP" == true ]]; then
        log INFO "Skipping backup (--no-backup flag set)"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would create backup at: $CURRENT_BACKUP"
        return 0
    fi

    if mkdir -p "$CURRENT_BACKUP"; then
        log ACTION "Backing up current deployment..."

        # Backup Python files
        for file in "${DEPLOY_FILES[@]}"; do
            if [[ -f "${APP_DIR}/${file}" ]]; then
                if cp "${APP_DIR}/${file}" "${CURRENT_BACKUP}/" 2>/dev/null; then
                    log INFO "Backed up: $file"
                else
                    log WARN "Failed to backup: $file"
                fi
            fi
        done

        # Backup display library
        if [[ -d "${APP_DIR}/display" ]]; then
            if cp -r "${APP_DIR}/display" "${CURRENT_BACKUP}/" 2>/dev/null; then
                log INFO "Backed up: display library"
            else
                log WARN "Failed to backup display library"
            fi
        fi

        # Store deployment info
        cat > "${CURRENT_BACKUP}/BACKUP_INFO.txt" << EOF
Backup Date: $(date '+%Y-%m-%d %H:%M:%S')
Backup Location: ${CURRENT_BACKUP}
Source: ${PROJECT_ROOT}
Deployment Version: $(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo 'unknown')
EOF

        log SUCCESS "Backup created: $CURRENT_BACKUP"
        return 0
    else
        log ERROR "Failed to create backup directory"
        return 1
    fi
}

# Check for git changes
check_git_status() {
    section_header "Checking Git Status"

    if [[ ! -d "${PROJECT_ROOT}/.git" ]]; then
        log WARN "Not a git repository (skipping version check)"
        return 0
    fi

    if git -C "$PROJECT_ROOT" diff-index --quiet HEAD -- 2>/dev/null; then
        log SUCCESS "Working tree clean"
    else
        if [[ "$FORCE" == true ]]; then
            log WARN "Uncommitted changes detected (--force flag set, proceeding anyway)"
        else
            log WARN "Uncommitted changes detected:"
            git -C "$PROJECT_ROOT" status --short 2>/dev/null | sed 's/^/  /'
            log INFO "Use --force to deploy with uncommitted changes"
            return 1
        fi
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
                log WARN "Failed to stop: $service (may not be running)"
            fi
        else
            log INFO "Service not running: $service"
        fi
    done

    # Give services time to shut down gracefully
    sleep 2

    return 0
}

# Deploy files
deploy_files() {
    section_header "Deploying Files"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would deploy files:"
        for file in "${DEPLOY_FILES[@]}"; do
            if [[ -f "${PROJECT_ROOT}/${file}" ]]; then
                log INFO "  - $file → $APP_DIR/"
            fi
        done

        # Check for display library
        if [[ -d "${PROJECT_ROOT}/display" ]]; then
            log INFO "  - display/ → $APP_DIR/"
        fi

        return 0
    fi

    local deploy_failed=false

    # Deploy Python files
    for file in "${DEPLOY_FILES[@]}"; do
        if [[ -f "${PROJECT_ROOT}/${file}" ]]; then
            log ACTION "Deploying $file..."
            if cp "${PROJECT_ROOT}/${file}" "${APP_DIR}/" 2>/dev/null; then
                log SUCCESS "Deployed: $file"
            else
                log ERROR "Failed to deploy: $file"
                deploy_failed=true
            fi
        else
            log WARN "Source file not found: ${PROJECT_ROOT}/${file}"
        fi
    done

    # Deploy display library
    if [[ -d "${PROJECT_ROOT}/display" ]]; then
        log ACTION "Deploying display library..."
        if cp -r "${PROJECT_ROOT}/display" "${APP_DIR}/" 2>/dev/null; then
            log SUCCESS "Deployed: display library"
        else
            log ERROR "Failed to deploy display library"
            deploy_failed=true
        fi
    fi

    if [[ "$deploy_failed" == true ]]; then
        return 1
    fi

    return 0
}

# Validate configuration
validate_configuration() {
    section_header "Validating Configuration"

    if [[ ! -f "${APP_DIR}/config.json" ]]; then
        log WARN "config.json not found"
        return 0
    fi

    if python3 -c "import json; json.load(open('${APP_DIR}/config.json'))" 2>/dev/null; then
        log SUCCESS "config.json is valid JSON"
    else
        log ERROR "config.json is invalid JSON"
        return 1
    fi

    return 0
}

# Set permissions
set_permissions() {
    section_header "Setting File Permissions"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would set permissions on: $APP_DIR"
        return 0
    fi

    if chmod -R 755 "${APP_DIR}" 2>/dev/null; then
        log SUCCESS "Set directory permissions: 755"
    else
        log WARN "Could not set all permissions"
    fi

    if chmod -R 644 "${APP_DIR}"/*.py "${APP_DIR}"/*.json 2>/dev/null; then
        log SUCCESS "Set file permissions: 644"
    else
        log WARN "Could not set file permissions"
    fi

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

    # Give services time to start
    sleep 3

    return 0
}

# Run health checks
run_health_checks() {
    section_header "Running Health Checks"

    if [[ "$SKIP_HEALTH_CHECK" == true ]]; then
        log INFO "Health check skipped"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would run health checks"
        return 0
    fi

    # Check if services are running
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log SUCCESS "Service healthy: $service"
        else
            log WARN "Service not running: $service"
        fi
    done

    # Check web server is accessible
    if curl -s http://localhost:5000 >/dev/null 2>&1; then
        log SUCCESS "Web server is responding"
    else
        log WARN "Web server may not be responding (network check required)"
    fi

    return 0
}

# Cleanup old backups
cleanup_old_backups() {
    section_header "Cleaning Up Old Backups"

    if [[ ! -d "$BACKUP_DIR" ]]; then
        return 0
    fi

    # Keep only the last 5 backups
    local backup_count=$(ls -d ${BACKUP_DIR}/backup_* 2>/dev/null | wc -l)
    if (( backup_count > 5 )); then
        log ACTION "Removing old backups (keeping 5 most recent)..."
        ls -d ${BACKUP_DIR}/backup_* | sort -r | tail -n +6 | while read old_backup; do
            log INFO "Removing: $(basename $old_backup)"
            rm -rf "$old_backup"
        done
    fi
}

# Print summary
print_summary() {
    section_header "Deployment Summary"

    echo -e "${GREEN}Deployment Complete!${NC}"
    echo ""
    echo "Deployment Details:"
    echo "  Project Root: ${PROJECT_ROOT}"
    echo "  App Directory: ${APP_DIR}"
    echo "  Backup Location: ${CURRENT_BACKUP}"
    echo "  Timestamp: ${BACKUP_TIMESTAMP}"
    echo ""
    echo "Status Checks:"
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            echo "  ✓ $service is running"
        else
            echo "  ✗ $service is NOT running"
        fi
    done
    echo ""
    echo "Next Steps:"
    echo "  1. Verify application functionality"
    echo "  2. Check logs: tail -f /var/log/pizero-app/webserver.log"
    echo "  3. Test web interface: http://192.168.50.202:5000"
    echo ""
    echo "To rollback, run: ./rollback.sh"
    echo "Log file: $LOG_FILE"
}

# Print error summary
print_error_summary() {
    section_header "Deployment Failed"

    echo -e "${RED}Deployment encountered errors!${NC}"
    echo ""
    echo "Actions taken:"
    if [[ -d "$CURRENT_BACKUP" ]]; then
        echo "  ✓ Backup created at: $CURRENT_BACKUP"
        echo "  • To restore: ./rollback.sh"
    fi
    echo ""
    echo "Next steps:"
    echo "  1. Review the log file for details:"
    echo "     cat $LOG_FILE"
    echo "  2. Fix the issues"
    echo "  3. Try deployment again"
    echo ""
    echo "Emergency rollback:"
    echo "  ./rollback.sh"
}

# Main execution
main() {
    local deploy_failed=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                SKIP_HEALTH_CHECK=true
                ;;
            --no-backup)
                NO_BACKUP=true
                ;;
            --force)
                FORCE=true
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
        shift
    done

    # Setup
    create_log_directory
    print_header

    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}DRY-RUN MODE ENABLED${NC} - No changes will be made"
        echo ""
    fi

    # Execution
    verify_app_directory || exit 1
    check_git_status || exit 1
    create_backup || exit 1
    stop_services || deploy_failed=true
    deploy_files || deploy_failed=true
    validate_configuration || deploy_failed=true
    set_permissions || deploy_failed=true
    start_services || deploy_failed=true
    run_health_checks || deploy_failed=true
    cleanup_old_backups

    # Summary
    if [[ "$deploy_failed" == true ]]; then
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
    --dry-run       Run without making any changes
    --no-backup     Skip creating backup before deployment
    --force         Deploy even with uncommitted git changes
    --quiet         Suppress output (log only)
    --help          Show this help message

Description:
    Deploys application updates with automatic backup and validation.
    Creates a timestamped backup before deploying.

Examples:
    ./$0                      # Deploy with backup
    ./$0 --dry-run            # Preview deployment
    ./$0 --force              # Deploy despite uncommitted changes
    ./$0 --no-backup --force  # Deploy without backup/checks

Rollback:
    ./rollback.sh             # Restore from most recent backup

Log file: ${LOG_FILE}

EOF
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
