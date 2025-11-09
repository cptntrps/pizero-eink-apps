#!/bin/bash

################################################################################
# Pi Zero 2W Systemd Services Installation Script
#
# This script installs and configures systemd services for Pi Zero 2W apps:
# - Menu System (pizero-menu.service)
# - Web Server API (pizero-web.service)
# - Medicine Tracker (pizero-medicine.service)
#
# Usage:
#   sudo ./install-services.sh [--start] [--enable] [--all]
#
# Options:
#   --start       Start services after installation
#   --enable      Enable services to start on boot (default: enabled)
#   --all         Install, enable, and start all services
#   --help        Display this help message
#
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SYSTEMD_DIR="$PROJECT_ROOT/systemd"
SYSTEM_SERVICES_DIR="/etc/systemd/system"

# Parse command line arguments
START_SERVICES=false
ENABLE_SERVICES=true
INSTALL_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --start)
            START_SERVICES=true
            shift
            ;;
        --enable)
            ENABLE_SERVICES=true
            shift
            ;;
        --all)
            INSTALL_ALL=true
            START_SERVICES=true
            ENABLE_SERVICES=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -E "^# " | sed 's/^# //g'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to verify service files exist
verify_files() {
    print_info "Verifying service files..."

    local files=(
        "$SYSTEMD_DIR/pizero-menu.service"
        "$SYSTEMD_DIR/pizero-web.service"
        "$SYSTEMD_DIR/pizero-medicine.service"
    )

    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Service file not found: $file"
            exit 1
        fi
        print_success "Found: $(basename $file)"
    done
}

# Function to install service files
install_services() {
    print_info "Installing service files to $SYSTEM_SERVICES_DIR..."

    local services=(
        "pizero-menu.service"
        "pizero-web.service"
        "pizero-medicine.service"
    )

    for service in "${services[@]}"; do
        local source="$SYSTEMD_DIR/$service"
        local dest="$SYSTEM_SERVICES_DIR/$service"

        print_info "Installing $service..."
        cp "$source" "$dest"
        chmod 644 "$dest"
        print_success "Installed: $service"
    done
}

# Function to reload systemd daemon
reload_systemd() {
    print_info "Reloading systemd daemon..."
    systemctl daemon-reload
    print_success "Systemd daemon reloaded"
}

# Function to enable services
enable_services() {
    print_info "Enabling services to start on boot..."

    local services=(
        "pizero-menu.service"
        "pizero-web.service"
        "pizero-medicine.service"
    )

    for service in "${services[@]}"; do
        print_info "Enabling $service..."
        systemctl enable "$service"
        print_success "Enabled: $service"
    done
}

# Function to start services
start_services() {
    print_info "Starting services..."

    local services=(
        "pizero-menu.service"
        "pizero-web.service"
        "pizero-medicine.service"
    )

    for service in "${services[@]}"; do
        print_info "Starting $service..."
        systemctl start "$service"
        print_success "Started: $service"
    done
}

# Function to display service status
show_status() {
    print_info "Service Status:"
    echo ""

    local services=(
        "pizero-menu.service"
        "pizero-web.service"
        "pizero-medicine.service"
    )

    for service in "${services[@]}"; do
        echo "--- $service ---"
        systemctl status "$service" --no-pager || true
        echo ""
    done
}

# Function to display usage information
show_usage() {
    cat << EOF

${BLUE}Systemd Services Installed Successfully${NC}

Installed Services:
  • pizero-menu.service    - Menu system for application selection
  • pizero-web.service     - Flask API web server
  • pizero-medicine.service - Medicine tracker application

Common Commands:
  # View service status
  sudo systemctl status pizero-menu.service
  sudo systemctl status pizero-web.service
  sudo systemctl status pizero-medicine.service

  # Start/stop services
  sudo systemctl start pizero-menu.service
  sudo systemctl stop pizero-menu.service
  sudo systemctl restart pizero-menu.service

  # View logs
  sudo journalctl -u pizero-menu.service -f
  sudo journalctl -u pizero-web.service -f
  sudo journalctl -u pizero-medicine.service -f

  # Enable/disable on boot
  sudo systemctl enable pizero-menu.service
  sudo systemctl disable pizero-menu.service

  # Reload systemd after modifying service files
  sudo systemctl daemon-reload

Configuration:
  Service files location: $SYSTEM_SERVICES_DIR/
  Log location: /var/log/syslog or use journalctl
  Documentation: $PROJECT_ROOT/docs/SYSTEMD_SERVICES.md

EOF
}

# Main execution
main() {
    echo ""
    print_info "Pi Zero 2W Systemd Services Installation Script"
    echo ""

    check_root
    verify_files
    install_services
    reload_systemd

    if [[ "$ENABLE_SERVICES" == true ]]; then
        enable_services
    fi

    if [[ "$START_SERVICES" == true ]]; then
        start_services
    fi

    echo ""
    show_status
    show_usage

    print_success "Installation complete!"
}

# Run main function
main
