#!/bin/bash

################################################################################
# Pi Zero 2W Medicine Tracking System - Installation Script
################################################################################
#
# Purpose: Install application and dependencies on fresh Raspberry Pi
# Usage:   ./install.sh [--dry-run]
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
LOG_FILE="${PROJECT_ROOT}/logs/install_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Application directories
APP_DIR="/home/pizero2w/pizero_apps"
PYTHON_LIB_DIR="/home/pizero2w/python/lib"
BACKUP_DIR="${APP_DIR}/backups"

# Application files
REQUIRED_FILES=(
    "medicine_app.py"
    "menu_button.py"
    "web_config.py"
    "config.json"
    "medicine_data.json"
)

# Python version requirement
REQUIRED_PYTHON_VERSION="3.7"

# ============================================================================
# COLORS & FORMATTING
# ============================================================================

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

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
            ERROR)   echo -e "${RED}[ERROR]${NC} ${message}" >&2 ;;
            WARN)    echo -e "${YELLOW}[WARN]${NC} ${message}" ;;
            INFO)    echo -e "${BLUE}[INFO]${NC} ${message}" ;;
            SUCCESS) echo -e "${GREEN}[✓]${NC} ${message}" ;;
            *)       echo "${message}" ;;
        esac
    fi
}

# Print header
print_header() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  Pi Zero 2W Medicine Tracking System - Installation Script    ║"
    echo "║  Version 1.0                                                  ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print section header
section_header() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log ERROR "This script must be run as root (use 'sudo ./install.sh')"
        return 1
    fi
    log SUCCESS "Running with appropriate privileges"
}

# Check system prerequisites
check_prerequisites() {
    section_header "Checking Prerequisites"
    local prereq_failed=false

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log ERROR "Python 3 is not installed"
        prereq_failed=true
    else
        local python_version=$(python3 --version 2>&1 | awk '{print $2}')
        log INFO "Python ${python_version} found"
    fi

    # Check required commands
    local required_commands=("pip3" "git" "systemctl" "wget")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log ERROR "Required command not found: $cmd"
            prereq_failed=true
        else
            log INFO "✓ $cmd available"
        fi
    done

    # Check if running on Raspberry Pi
    if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
        log WARN "Not running on Raspberry Pi (detected: $(cat /proc/device-tree/model 2>/dev/null || echo 'unknown'))"
    else
        log SUCCESS "Detected Raspberry Pi: $(cat /proc/device-tree/model)"
    fi

    # Check disk space
    local available_space=$(df /home | tail -1 | awk '{print $4}')
    if (( available_space < 102400 )); then  # Less than 100MB
        log WARN "Low disk space available: ${available_space}KB"
    else
        log INFO "Disk space available: ${available_space}KB"
    fi

    if [[ "$prereq_failed" == true ]]; then
        return 1
    fi

    log SUCCESS "All prerequisites satisfied"
}

# Update system packages
update_system() {
    section_header "Updating System Packages"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would execute: apt-get update && apt-get upgrade -y"
        return 0
    fi

    log INFO "Running apt-get update..."
    if apt-get update >/dev/null 2>&1; then
        log SUCCESS "System packages updated"
    else
        log ERROR "Failed to update system packages"
        return 1
    fi
}

# Install Python dependencies
install_python_dependencies() {
    section_header "Installing Python Dependencies"

    local python_packages=(
        "Flask==2.3.3"
        "requests==2.31.0"
        "Pillow==10.0.0"
        "RPi.GPIO==0.7.0"
        "numpy==1.21.6"
    )

    for package in "${python_packages[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            log INFO "[DRY-RUN] Would install: pip3 install $package"
        else
            log INFO "Installing ${package%%=*}..."
            if pip3 install "$package" --quiet >/dev/null 2>&1; then
                log SUCCESS "Installed ${package%%=*}"
            else
                log ERROR "Failed to install ${package%%=*}"
                return 1
            fi
        fi
    done

    return 0
}

# Create application directories
create_directories() {
    section_header "Creating Application Directories"

    local directories=(
        "$APP_DIR"
        "$BACKUP_DIR"
        "/var/log/pizero-app"
        "/tmp/pizero-tmp"
    )

    for dir in "${directories[@]}"; do
        if [[ "$DRY_RUN" == true ]]; then
            log INFO "[DRY-RUN] Would create directory: $dir"
        else
            if mkdir -p "$dir" 2>/dev/null; then
                log SUCCESS "Created directory: $dir"
            else
                log ERROR "Failed to create directory: $dir"
                return 1
            fi
        fi
    done

    return 0
}

# Deploy application files
deploy_application() {
    section_header "Deploying Application Files"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would copy application files from ${PROJECT_ROOT} to ${APP_DIR}"
        log INFO "[DRY-RUN] Files to copy:"
        for file in "${REQUIRED_FILES[@]}"; do
            log INFO "  - ${file}"
        done
        return 0
    fi

    # Copy all Python files
    local python_files=("${PROJECT_ROOT}"/*.py)
    for file in "${python_files[@]}"; do
        if [[ -f "$file" ]]; then
            local filename=$(basename "$file")
            if cp "$file" "${APP_DIR}/${filename}"; then
                log SUCCESS "Deployed: $filename"
            else
                log ERROR "Failed to deploy: $filename"
                return 1
            fi
        fi
    done

    # Copy display library
    if [[ -d "${PROJECT_ROOT}/display" ]]; then
        if cp -r "${PROJECT_ROOT}/display" "${APP_DIR}/"; then
            log SUCCESS "Deployed: display library"
        else
            log ERROR "Failed to deploy display library"
            return 1
        fi
    fi

    # Copy configuration files
    for file in config.json medicine_data.json; do
        if [[ -f "${PROJECT_ROOT}/${file}" ]]; then
            if cp "${PROJECT_ROOT}/${file}" "${APP_DIR}/"; then
                log SUCCESS "Deployed: $file"
            else
                log ERROR "Failed to deploy: $file"
                return 1
            fi
        else
            log WARN "Configuration file not found: ${PROJECT_ROOT}/${file}"
        fi
    done

    return 0
}

# Set file permissions
set_permissions() {
    section_header "Setting File Permissions"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would set permissions on ${APP_DIR}"
        return 0
    fi

    if chown -R pizero2w:pizero2w "$APP_DIR" 2>/dev/null; then
        log SUCCESS "Set ownership: pizero2w:pizero2w"
    else
        log WARN "Could not set ownership (user may not exist)"
    fi

    if chmod -R 755 "${APP_DIR}" 2>/dev/null; then
        log SUCCESS "Set directory permissions: 755"
    else
        log ERROR "Failed to set permissions"
        return 1
    fi

    if chmod -R 644 "${APP_DIR}"/*.{py,json} 2>/dev/null; then
        log SUCCESS "Set file permissions: 644"
    else
        log WARN "Could not set all file permissions"
    fi

    return 0
}

# Create systemd services
create_systemd_services() {
    section_header "Creating Systemd Services"

    if [[ "$DRY_RUN" == true ]]; then
        log INFO "[DRY-RUN] Would create systemd service files"
        return 0
    fi

    # Create web server service
    cat > /etc/systemd/system/pizero-webserver.service << 'EOF'
[Unit]
Description=Pi Zero Medicine Tracker Web Server
After=network.target

[Service]
Type=simple
User=pizero2w
WorkingDirectory=/home/pizero2w/pizero_apps
ExecStart=/usr/bin/python3 /home/pizero2w/pizero_apps/web_config.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/pizero-app/webserver.log
StandardError=append:/var/log/pizero-app/webserver.log

[Install]
WantedBy=multi-user.target
EOF

    if [[ $? -eq 0 ]]; then
        log SUCCESS "Created systemd service: pizero-webserver.service"
    else
        log ERROR "Failed to create systemd service"
        return 1
    fi

    # Create menu service
    cat > /etc/systemd/system/pizero-menu.service << 'EOF'
[Unit]
Description=Pi Zero Medicine Tracker Menu System
After=network.target

[Service]
Type=simple
User=pizero2w
WorkingDirectory=/home/pizero2w/pizero_apps
ExecStart=/usr/bin/python3 /home/pizero2w/pizero_apps/menu_button.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/pizero-app/menu.log
StandardError=append:/var/log/pizero-app/menu.log

[Install]
WantedBy=multi-user.target
EOF

    if [[ $? -eq 0 ]]; then
        log SUCCESS "Created systemd service: pizero-menu.service"
    else
        log ERROR "Failed to create menu service"
        return 1
    fi

    # Reload systemd
    if systemctl daemon-reload >/dev/null 2>&1; then
        log SUCCESS "Reloaded systemd daemon"
    else
        log WARN "Could not reload systemd daemon"
    fi

    return 0
}

# Verify installation
verify_installation() {
    section_header "Verifying Installation"
    local verification_failed=false

    # Check application directory
    if [[ -d "$APP_DIR" ]]; then
        log SUCCESS "Application directory exists: $APP_DIR"
    else
        log ERROR "Application directory missing: $APP_DIR"
        verification_failed=true
    fi

    # Check Python files
    for file in "${REQUIRED_FILES[@]}"; do
        if [[ -f "${APP_DIR}/${file}" ]]; then
            log SUCCESS "Found: $file"
        else
            log WARN "Missing: $file (may be created at runtime)"
        fi
    done

    # Check Python packages
    python3 -c "import flask" 2>/dev/null && log SUCCESS "Flask module available" || log WARN "Flask not available"
    python3 -c "import PIL" 2>/dev/null && log SUCCESS "Pillow module available" || log WARN "Pillow not available"

    if [[ "$verification_failed" == true ]]; then
        return 1
    fi

    log SUCCESS "Installation verification complete"
}

# Cleanup function
cleanup() {
    log INFO "Cleaning up temporary files..."
    rm -f /tmp/pizero-install-* 2>/dev/null || true
}

# Print summary
print_summary() {
    section_header "Installation Summary"

    echo -e "${GREEN}Installation Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Copy application files to ${APP_DIR}"
    echo "2. Verify configuration in config.json"
    echo "3. Start services:"
    echo "   sudo systemctl start pizero-webserver"
    echo "   sudo systemctl start pizero-menu"
    echo "4. Enable auto-start (optional):"
    echo "   sudo systemctl enable pizero-webserver"
    echo "   sudo systemctl enable pizero-menu"
    echo "5. Check web interface at http://192.168.50.202:5000"
    echo ""
    echo "Log file: $LOG_FILE"
}

# Print error summary
print_error_summary() {
    section_header "Installation Failed"

    echo -e "${RED}Installation encountered errors!${NC}"
    echo ""
    echo "Please review the log file for details:"
    echo "  cat $LOG_FILE"
    echo ""
    echo "Common issues:"
    echo "1. Missing prerequisites - ensure Python 3, pip3, and git are installed"
    echo "2. Permission issues - run with 'sudo'"
    echo "3. Network issues - check internet connectivity"
    echo "4. Disk space - ensure at least 100MB available"
}

# Main execution
main() {
    local install_failed=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                log INFO "Running in DRY-RUN mode (no changes will be made)"
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
    check_root || exit 1
    check_prerequisites || exit 1
    update_system || install_failed=true
    install_python_dependencies || install_failed=true
    create_directories || install_failed=true
    deploy_application || install_failed=true
    set_permissions || install_failed=true
    create_systemd_services || install_failed=true
    verify_installation || install_failed=true
    cleanup

    # Summary
    if [[ "$install_failed" == true ]]; then
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
    --quiet         Suppress output (log only)
    --help          Show this help message

Description:
    Installs the Pi Zero 2W Medicine Tracking System and all dependencies.
    Must be run with sudo privileges.

Example:
    sudo $0
    sudo $0 --dry-run
    sudo $0 --quiet

Log file: ${LOG_FILE}

EOF
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
