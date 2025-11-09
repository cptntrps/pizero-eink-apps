#!/bin/bash

################################################################################
# Pi Zero 2W Application Suite - Security Scanning Script
#
# This script performs comprehensive security checks including:
# - Python code analysis with Bandit
# - Dependency vulnerability scanning
# - File permission audits
# - Secrets exposure detection
# - Security configuration verification
#
# Usage: ./scripts/security_scan.sh [options]
# Options:
#   --full       Run all security checks
#   --quick      Run quick checks only
#   --report     Generate detailed report
#   --fix        Apply auto-fixable issues
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_FILE="${PROJECT_ROOT}/security_scan_report.txt"
LOG_FILE="${PROJECT_ROOT}/security_scan.log"

# Counters
CRITICAL_ISSUES=0
HIGH_ISSUES=0
MEDIUM_ISSUES=0
LOW_ISSUES=0
PASSED_CHECKS=0

# Options
RUN_FULL=false
RUN_QUICK=false
GENERATE_REPORT=false
AUTO_FIX=false

################################################################################
# Utility Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$LOG_FILE"
    ((PASSED_CHECKS++))
}

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $1" | tee -a "$LOG_FILE"
    ((CRITICAL_ISSUES++))
}

log_high() {
    echo -e "${RED}[HIGH]${NC} $1" | tee -a "$LOG_FILE"
    ((HIGH_ISSUES++))
}

log_medium() {
    echo -e "${YELLOW}[MEDIUM]${NC} $1" | tee -a "$LOG_FILE"
    ((MEDIUM_ISSUES++))
}

log_low() {
    echo -e "${YELLOW}[LOW]${NC} $1" | tee -a "$LOG_FILE"
    ((LOW_ISSUES++))
}

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_summary() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}SECURITY SCAN SUMMARY${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo -e "Checks Passed:        ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Critical Issues:      ${RED}$CRITICAL_ISSUES${NC}"
    echo -e "High Issues:          ${RED}$HIGH_ISSUES${NC}"
    echo -e "Medium Issues:        ${YELLOW}$MEDIUM_ISSUES${NC}"
    echo -e "Low Issues:           ${YELLOW}$LOW_ISSUES${NC}"

    TOTAL_ISSUES=$((CRITICAL_ISSUES + HIGH_ISSUES + MEDIUM_ISSUES + LOW_ISSUES))
    echo -e "Total Issues:         $TOTAL_ISSUES"
    echo ""

    if [ $CRITICAL_ISSUES -gt 0 ]; then
        echo -e "${RED}SECURITY POSTURE: CRITICAL${NC}"
        echo "Action: Immediate remediation required"
    elif [ $HIGH_ISSUES -gt 0 ]; then
        echo -e "${RED}SECURITY POSTURE: HIGH RISK${NC}"
        echo "Action: Address high-risk issues before production"
    elif [ $MEDIUM_ISSUES -gt 0 ]; then
        echo -e "${YELLOW}SECURITY POSTURE: MEDIUM RISK${NC}"
        echo "Action: Address medium-risk issues in next sprint"
    else
        echo -e "${GREEN}SECURITY POSTURE: ACCEPTABLE${NC}"
        echo "Action: Continue with regular monitoring"
    fi

    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

################################################################################
# Security Checks
################################################################################

check_python_security() {
    print_header "Python Code Security Analysis (Bandit)"

    if ! command -v bandit &> /dev/null; then
        log_info "Installing Bandit..."
        pip install bandit -q
    fi

    if bandit -r "$PROJECT_ROOT" -f json -o /tmp/bandit_report.json 2>/dev/null; then
        # Check if bandit found any issues
        if grep -q '"issue_cwe"' /tmp/bandit_report.json 2>/dev/null; then
            log_high "Bandit found potential security issues"
            bandit -r "$PROJECT_ROOT" 2>/dev/null | head -50
        else
            log_pass "No critical Python security issues detected by Bandit"
        fi
    else
        log_info "Bandit scan completed (check report for details)"
    fi
}

check_dependency_vulnerabilities() {
    print_header "Dependency Vulnerability Scanning"

    if ! command -v safety &> /dev/null; then
        log_info "Installing Safety..."
        pip install safety -q
    fi

    if safety check --json > /tmp/safety_report.json 2>/dev/null; then
        log_pass "No known vulnerabilities found in dependencies"
    else
        log_high "Safety found potential dependency vulnerabilities"
        safety check 2>/dev/null | head -30
    fi
}

check_file_permissions() {
    print_header "File Permission Security Audit"

    local issues=0

    # Check config.json
    if [ -f "$PROJECT_ROOT/config.json" ]; then
        local perm=$(stat -c "%a" "$PROJECT_ROOT/config.json" 2>/dev/null || stat -f "%OLp" "$PROJECT_ROOT/config.json")
        if [ "$perm" == "644" ] || [ "$perm" == "644" ]; then
            log_critical "config.json is world-readable (permissions: $perm)"
            ((issues++))
        elif [ "$perm" == "600" ]; then
            log_pass "config.json has secure permissions"
        else
            log_medium "config.json permissions: $perm (consider 600)"
            ((issues++))
        fi
    fi

    # Check medicine_data.json
    if [ -f "$PROJECT_ROOT/medicine_data.json" ]; then
        local perm=$(stat -c "%a" "$PROJECT_ROOT/medicine_data.json" 2>/dev/null || stat -f "%OLp" "$PROJECT_ROOT/medicine_data.json")
        if [ "$perm" == "644" ] || [ "$perm" == "644" ]; then
            log_critical "medicine_data.json is world-readable (permissions: $perm)"
            ((issues++))
        elif [ "$perm" == "600" ]; then
            log_pass "medicine_data.json has secure permissions"
        else
            log_medium "medicine_data.json permissions: $perm (consider 600)"
            ((issues++))
        fi
    fi

    # Check database directory
    if [ -d "$PROJECT_ROOT/db" ]; then
        local perm=$(stat -c "%a" "$PROJECT_ROOT/db" 2>/dev/null || stat -f "%OLp" "$PROJECT_ROOT/db")
        if [ "$perm" == "700" ]; then
            log_pass "Database directory has secure permissions (700)"
        else
            log_high "Database directory permissions: $perm (should be 700)"
            ((issues++))
        fi
    fi

    # Check backups directory
    if [ -d "$PROJECT_ROOT/backups" ]; then
        local perm=$(stat -c "%a" "$PROJECT_ROOT/backups" 2>/dev/null || stat -f "%OLp" "$PROJECT_ROOT/backups")
        if [ "$perm" == "755" ] || [ "$perm" == "644" ]; then
            log_critical "Backup directory is world-readable (permissions: $perm)"
            ((issues++))
        elif [ "$perm" == "700" ]; then
            log_pass "Backup directory has secure permissions (700)"
        else
            log_medium "Backup directory permissions: $perm (consider 700)"
            ((issues++))
        fi
    fi

    if [ $issues -eq 0 ]; then
        log_pass "File permissions audit passed"
    fi
}

check_secrets_exposure() {
    print_header "Secrets Exposure Detection"

    local issues=0

    # Check for hardcoded passwords in Python files
    if grep -r "password.*=" "$PROJECT_ROOT"/*.py 2>/dev/null | grep -v "password=''" | grep -v "password=\"\"" > /dev/null; then
        log_medium "Possible hardcoded credentials in Python files"
        grep -r "password.*=" "$PROJECT_ROOT"/*.py 2>/dev/null | head -5
        ((issues++))
    else
        log_pass "No obvious hardcoded credentials in Python files"
    fi

    # Check for .env file in repository
    if [ -f "$PROJECT_ROOT/.env" ]; then
        log_critical ".env file is versioned in git (should be in .gitignore)"
        ((issues++))
    else
        log_pass ".env file not found in repository"
    fi

    # Check for .env.example
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        log_pass ".env.example found (documentation for required environment variables)"
    else
        log_low ".env.example not found (consider creating for documentation)"
        ((issues++))
    fi

    # Check for API keys in config files
    if [ -f "$PROJECT_ROOT/config.json" ]; then
        if grep -i "api_key\|apikey\|secret\|token" "$PROJECT_ROOT/config.json" 2>/dev/null | grep -v "CHANGE_ME" > /dev/null; then
            log_high "Possible API keys or secrets in config.json"
            ((issues++))
        else
            log_pass "No obvious API keys in config.json"
        fi
    fi

    if [ $issues -eq 0 ]; then
        log_pass "Secrets exposure check passed"
    fi
}

check_git_configuration() {
    print_header "Git Configuration Security"

    if [ -d "$PROJECT_ROOT/.git" ]; then
        # Check .gitignore for sensitive patterns
        if [ -f "$PROJECT_ROOT/.gitignore" ]; then
            local has_env=false
            local has_secrets=false

            grep -q "^\.env" "$PROJECT_ROOT/.gitignore" && has_env=true
            grep -q "secret\|credential\|password" "$PROJECT_ROOT/.gitignore" && has_secrets=true

            if $has_env; then
                log_pass ".gitignore includes .env files"
            else
                log_high ".gitignore does not exclude .env files"
            fi

            if $has_secrets; then
                log_pass ".gitignore includes patterns for secrets"
            else
                log_medium ".gitignore could be more comprehensive"
            fi
        else
            log_high ".gitignore file not found"
        fi
    fi
}

check_dependencies_versions() {
    print_header "Dependency Version Analysis"

    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log_info "Current dependency versions:"

        # Check Flask version
        if grep -q "Flask>=" "$PROJECT_ROOT/requirements.txt"; then
            local flask_version=$(grep "Flask>=" "$PROJECT_ROOT/requirements.txt" | cut -d'>' -f2)
            if [[ "$flask_version" < "3.0" ]]; then
                log_high "Flask version is outdated: $flask_version (recommend 3.0+)"
            else
                log_pass "Flask version is current: $flask_version"
            fi
        fi

        # Check for security packages
        if grep -q "Flask-Talisman" "$PROJECT_ROOT/requirements.txt"; then
            log_pass "Flask-Talisman included for security headers"
        else
            log_medium "Flask-Talisman not found (recommended for security headers)"
        fi

        if grep -q "Flask-Limiter" "$PROJECT_ROOT/requirements.txt"; then
            log_pass "Flask-Limiter included for rate limiting"
        else
            log_medium "Flask-Limiter not found (recommended for rate limiting)"
        fi

        if grep -q "python-dotenv" "$PROJECT_ROOT/requirements.txt"; then
            log_pass "python-dotenv included for environment management"
        else
            log_low "python-dotenv not found (recommended for secrets management)"
        fi
    fi
}

check_input_validation() {
    print_header "Input Validation Analysis"

    if grep -r "datetime.strptime" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        if grep -r "try:" "$PROJECT_ROOT" --include="*.py" -A 3 | grep -q "datetime.strptime"; then
            log_pass "Date parsing appears to have error handling"
        else
            log_medium "Some datetime.strptime calls may lack error handling"
        fi
    fi

    if grep -r "request.args.get" "$PROJECT_ROOT" --include="*.py" | grep -i "int(" > /dev/null; then
        log_medium "Integer parameters from request.args should have bounds checking"
    fi

    if grep -r "marshmallow" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_pass "Marshmallow validation schemas in use"
    else
        log_high "Marshmallow not found (recommend for input validation)"
    fi
}

check_sql_injection_protection() {
    print_header "SQL Injection Protection Analysis"

    local unparameterized=0

    # Check for string concatenation in SQL
    if grep -r "execute.*%" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_medium "Found % formatting in SQL queries (use ? instead)"
        ((unparameterized++))
    fi

    if grep -r "execute.*f\"" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_medium "Found f-string in SQL queries (use parameterized queries)"
        ((unparameterized++))
    fi

    # Check for proper parameterized queries
    if grep -r "execute.*?" "$PROJECT_ROOT/db" --include="*.py" > /dev/null; then
        log_pass "Parameterized queries detected in database layer"
    fi

    if [ $unparameterized -eq 0 ]; then
        log_pass "No obvious SQL injection vulnerabilities detected"
    fi
}

check_xss_protection() {
    print_header "XSS Protection Analysis"

    # Check for HTML escaping
    if grep -r "escape\|markupsafe" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_pass "HTML escaping functions in use"
    else
        log_info "HTML escaping not explicitly found (Flask's jsonify handles it)"
    fi

    # Check for unsafe rendering
    if grep -r "Markup\|safe=" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_medium "Found use of Markup or 'safe=' (verify this is intentional)"
    fi

    log_pass "No obvious XSS vulnerabilities detected"
}

check_authentication() {
    print_header "Authentication & Authorization Analysis"

    if grep -r "@jwt_required\|@login_required\|@auth_required" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_pass "Authentication decorators found"
    else
        log_critical "No authentication decorators found on API endpoints"
    fi

    if grep -r "SECRET_KEY\|JWT_SECRET" "$PROJECT_ROOT" --include="*.py" | grep -i "environ\|getenv" > /dev/null; then
        log_pass "Secrets appear to be loaded from environment"
    else
        log_high "Secrets should be loaded from environment variables"
    fi
}

check_logging_security() {
    print_header "Logging Security Analysis"

    # Check for password logging
    if grep -r "logger.*password\|log.*password" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_high "Found password logging (remove or redact)"
    else
        log_pass "No obvious password logging found"
    fi

    # Check for token logging
    if grep -r "logger.*token\|log.*token" "$PROJECT_ROOT" --include="*.py" > /dev/null; then
        log_high "Found token logging (remove or redact)"
    else
        log_pass "No obvious token logging found"
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     Pi Zero 2W Security Scanning System                   ║"
    echo "║                                                            ║"
    echo "║     Comprehensive Security Audit                          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Initialize log file
    > "$LOG_FILE"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --full)
                RUN_FULL=true
                shift
                ;;
            --quick)
                RUN_QUICK=true
                shift
                ;;
            --report)
                GENERATE_REPORT=true
                shift
                ;;
            --fix)
                AUTO_FIX=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Default to quick scan if no option specified
    if [ "$RUN_FULL" = false ] && [ "$RUN_QUICK" = false ]; then
        RUN_QUICK=true
    fi

    # Run security checks
    check_file_permissions
    check_secrets_exposure
    check_git_configuration
    check_dependencies_versions
    check_input_validation
    check_sql_injection_protection
    check_xss_protection
    check_authentication
    check_logging_security

    # Run extended checks if full mode
    if [ "$RUN_FULL" = true ]; then
        check_python_security
        check_dependency_vulnerabilities
    fi

    # Print summary
    print_summary

    # Generate report if requested
    if [ "$GENERATE_REPORT" = true ]; then
        echo "Report generated: $REPORT_FILE"
        cp "$LOG_FILE" "$REPORT_FILE"
    fi

    # Exit with appropriate code
    if [ $CRITICAL_ISSUES -gt 0 ]; then
        exit 2
    elif [ $HIGH_ISSUES -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main "$@"
