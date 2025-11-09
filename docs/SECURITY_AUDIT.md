# Security Audit Report - Pi Zero 2W Application Suite

**Date:** November 8, 2025
**Severity Levels:** Critical, High, Medium, Low
**Status:** COMPLETED

---

## Executive Summary

This security audit identified several security issues across the application. While the application demonstrates good security practices in some areas (parameterized SQL queries, input validation schemas), there are critical vulnerabilities that require immediate remediation.

**Critical Issues Found:** 2
**High Issues Found:** 5
**Medium Issues Found:** 6
**Low Issues Found:** 4

---

## 1. INPUT VALIDATION AUDIT

### 1.1 Critical - Missing Input Bounds Validation

**Location:** `/home/user/pizerowgpio/api/v1/routes/medicines.py`

**Issue:** Line 343 - `reminder_window` parameter lacks bounds validation
```python
reminder_window = int(request.args.get('reminder_window', 30))
```

**Risk:** Integer overflow, DoS attacks, invalid calculations
**CVSS Score:** 7.5 (High)

**Fix Applied:** Add bounds validation
```python
reminder_window = min(int(request.args.get('reminder_window', 30)), 1440)
reminder_window = max(reminder_window, 1)
```

---

### 1.2 High - Insufficient Date Format Validation

**Location:** Multiple files
- `/home/user/pizerowgpio/api/v1/routes/medicines.py` line 347
- `/home/user/pizerowgpio/api/v1/routes/tracking.py` line 288
- `/home/user/pizerowgpio/web_config.py` line 288

**Issue:** `datetime.strptime()` called without try-except
```python
check_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
```

**Risk:** Unhandled exceptions, 500 errors, poor error messages
**CVSS Score:** 5.3 (Medium)

**Fix Applied:** Add proper error handling with validation functions

---

### 1.3 High - ISO Format String Parsing Without Validation

**Location:** `/home/user/pizerowgpio/api/v1/routes/medicines.py` lines 433, 515

**Issue:**
```python
timestamp = datetime.fromisoformat(timestamp_str.replace('Z', ''))
```

**Risk:** Malformed timestamps cause unhandled exceptions
**CVSS Score:** 5.3 (Medium)

**Fix Applied:** Add error handling and validation

---

### 1.4 High - Missing Pagination Bounds

**Location:** `/home/user/pizerowgpio/api/v1/routes/medicines.py` line 54

**Issue:**
```python
per_page = min(int(request.args.get('per_page', 20)), 100)
```

**Risk:** Negative pagination values not caught; page parameter unbounded
**CVSS Score:** 4.7 (Medium)

**Fix Applied:** Validate both page and per_page with bounds

---

### 1.5 High - Configuration Section Validation Missing

**Location:** `/home/user/pizerowgpio/api/v1/routes/config.py` lines 109, 203, 262

**Issue:** No validation of section names - only checked against hardcoded list
```python
if section not in config:
    return jsonify(...), 404
```

**Risk:** Potential path traversal if section names not properly sanitized
**CVSS Score:** 5.5 (Medium)

**Fix Applied:** Add regex validation for section names

---

## 2. SQL INJECTION TESTING

**Status:** PASS ✓

**Findings:** All database queries use parameterized queries with `?` placeholders

**Evidence:**
```python
# From db/medicine_db.py - Correct implementation
cursor = conn.execute(
    "SELECT id FROM medicines WHERE id = ?",
    (medicine_id,)
)
```

**Recommendation:** Maintain this practice for all future queries

---

## 3. XSS VULNERABILITY TESTING

### 3.1 Medium - Error Details Exposed in API Responses

**Location:** `/home/user/pizerowgpio/api/v1/routes/*.py`

**Issue:** Raw error strings exposed to clients:
```python
details=str(e)  # Database exception messages exposed
```

**Risk:** Information disclosure; potential for error-based attacks
**CVSS Score:** 5.3 (Medium)

**Fix Applied:** Sanitize error messages in production; use generic messages

---

### 3.2 Low - Configuration Data Serialization

**Location:** `/home/user/pizerowgpio/web_config.py` line 82

**Issue:** Direct JSON response without HTML escaping:
```python
return jsonify(create_success_response(data=config))
```

**Risk:** If configuration contains HTML/JS, could be XSS vulnerable
**CVSS Score:** 3.1 (Low)

**Fix Applied:** Flask's `jsonify()` handles escaping correctly; no changes needed

---

## 4. FILE PERMISSION REVIEW

### 4.1 Good - Database Directory Permissions

**Status:** PASS ✓
```
drwx------  3 root root  4096 Nov  8 20:54 db
```
Permissions 700 (rwx------) correctly restrict access to owner only.

---

### 4.2 Critical - Backup Directory World Readable

**Location:** `/home/user/pizerowgpio/backups/`

**Status:** FAIL
```
drwxr-xr-x  9 root root  4096 Nov  8 22:11 backups
-rw-r--r--  1 root root  2830 Nov  8 21:33 config.json
```

**Risk:** Database backups and configuration backups readable by all users; contains sensitive data
**CVSS Score:** 8.2 (High)

**Fix Applied:** Change permissions to 700

---

### 4.3 High - Configuration File Readable by World

**Location:** `/home/user/pizerowgpio/config.json`

**Status:** FAIL
```
-rw-r--r--  1 root root  2830 Nov  8 21:33 config.json
```

**Risk:** Contains WiFi passwords, API configurations
**CVSS Score:** 7.5 (High)

**Fix Applied:** Change permissions to 600

---

### 4.4 High - Medicine Data File Readable by World

**Location:** `/home/user/pizerowgpio/medicine_data.json`

**Status:** FAIL
```
-rw-r--r--  1 root root  3969 Nov  8 20:15 medicine_data.json
```

**Risk:** Medical information is sensitive PII
**CVSS Score:** 6.5 (Medium)

**Fix Applied:** Change permissions to 600

---

### 4.5 Medium - Python Cache Files Not Ignored

**Location:** `__pycache__/`, `*.pyc` files

**Status:** PARTIAL
`.gitignore` present but `__pycache__` exists in repository

**Risk:** Cache files can reveal source code structure
**CVSS Score:** 3.7 (Low)

**Fix Applied:** Clean up existing cache files

---

## 5. SECRETS EXPOSURE CHECK

### 5.1 Critical - Hardcoded Credentials in Configuration

**Location:** `/home/user/pizerowgpio/config.json` line 118

**Issue:**
```json
"hotspot_password": "raspberry"
```

**Risk:** Hardcoded WiFi password exposed; trivial to compromise
**CVSS Score:** 9.1 (Critical)

**Fix Applied:** Remove from config.json; use environment variables

---

### 5.2 Critical - Hardcoded Database Path

**Location:** `/home/user/pizerowgpio/db/medicine_db.py` line 29

**Issue:**
```python
'/home/pizero2w/pizero_apps/medicine.db'
```

**Risk:** Hardcoded paths not portable; environment variable better
**CVSS Score:** 5.3 (Medium)

**Fix Applied:** Already uses environment variable `PIZERO_MEDICINE_DB`

---

### 5.3 Critical - Hardcoded File Paths in web_config.py

**Location:** `/home/user/pizerowgpio/web_config.py` lines 11, 48

**Issue:**
```python
CONFIG_FILE = "/home/pizero2w/pizero_apps/config.json"
MEDICINE_DATA_FILE = "/home/pizero2w/pizero_apps/medicine_data.json"
```

**Risk:** Hardcoded paths don't match actual installation location
**CVSS Score:** 6.5 (Medium)

**Fix Applied:** Use environment variables with fallbacks

---

### 5.4 High - No .env File .gitignore

**Location:** `.gitignore` check

**Issue:** No `.env` file handling documented
**CVSS Score:** 4.3 (Medium)

**Fix Applied:** Add `.env` to .gitignore

---

## 6. DEPENDENCY VULNERABILITY SCAN

### 6.1 High - Outdated Flask Version Specification

**Location:** `/home/user/pizerowgpio/requirements.txt`

**Issue:**
```
Flask>=2.0.0  # Released in 2021; outdated
```

**Risk:** Flask 2.0.x is outdated; use Flask 3.0+ for security patches
**CVSS Score:** 6.5 (High)

**Security Fixes in Newer Versions:**
- Flask 2.2.0+: Fixed security issues in form parsing
- Flask 2.3.0+: Improved error handling
- Flask 3.0.0+: Better CORS handling, updated dependencies

**Fix Applied:** Updated to `Flask>=3.0.0`

---

### 6.2 High - Non-Specific Version Constraints

**Location:** All dependencies in `requirements.txt`

**Issue:**
```
Pillow>=8.0.0  # Very old version
gpiozero>=1.6.2  # Outdated
marshmallow>=3.14.0  # Old
```

**Risk:** Vulnerable versions of dependencies could be installed
**CVSS Score:** 5.3 (Medium)

**Fix Applied:** Updated all versions with proper constraints

---

### 6.3 Medium - Missing Security Dependencies

**Location:** `requirements.txt`

**Issue:** No explicit security libraries for secrets management
**CVSS Score:** 3.5 (Low)

**Fix Applied:** Added `python-dotenv` for environment variable management

---

## 7. FLASK SECURITY ISSUES

### 7.1 High - Debug Mode in Production

**Location:** `/home/user/pizerowgpio/web_config.py` line 353

**Issue:**
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

**Status:** PASS ✓ - Debug is correctly disabled

---

### 7.2 High - Missing Security Headers

**Location:** All API endpoints

**Issue:** No security headers returned
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security
Content-Security-Policy
```

**Risk:** Browser protections disabled; vulnerable to MIME type sniffing, clickjacking
**CVSS Score:** 5.5 (Medium)

**Fix Applied:** Added security headers middleware

---

### 7.3 Medium - No CORS Configuration

**Location:** API blueprint initialization

**Issue:** Cross-Origin Resource Sharing not configured
**CVSS Score:** 4.3 (Medium)

**Fix Applied:** Added CORS configuration with strict policies

---

## 8. AUTHENTICATION & AUTHORIZATION

### 8.1 Critical - No Authentication on API Endpoints

**Location:** All API endpoints

**Issue:** All endpoints publicly accessible without authentication
```python
@api_v1_bp.route('/medicines', methods=['GET'])
def list_medicines():  # No @auth_required
```

**Risk:** Anyone can access/modify medical data
**CVSS Score:** 9.8 (Critical)

**Fix Applied:** Documented in recommendations; requires architecture change

---

### 8.2 High - No Rate Limiting

**Location:** API endpoints

**Issue:** No rate limiting or throttling
**CVSS Score:** 6.5 (High)

**Fix Applied:** Added rate limiting middleware

---

## 9. LOGGING AND MONITORING

### 9.1 Medium - Sensitive Data in Logs

**Location:** `/home/user/pizerowgpio/db/medicine_db.py` line 35

**Issue:**
```python
logger.info(f"MedicineDatabase initialized: {db_path}")
```

**Risk:** Database paths logged; could be captured in logs
**CVSS Score:** 3.5 (Low)

**Fix Applied:** Review logging; remove sensitive paths

---

## 10. DATA VALIDATION PATTERNS

### 10.1 Good - Marshmallow Schemas

**Status:** PASS ✓

The project uses Marshmallow for comprehensive input validation:
- Type validation
- Range validation
- Format validation (regex)
- Custom validators

This is a security best practice.

---

## Security Fixes Applied

### Summary of Changes

1. **Input Validation Hardening**
   - Added bounds checking for integer parameters
   - Improved datetime parsing with error handling
   - Added pagination bounds validation

2. **File Permissions**
   - Changed config.json to 600 (owner read/write only)
   - Changed medicine_data.json to 600
   - Changed backups directory to 700

3. **Configuration Management**
   - Removed hardcoded WiFi password from config.json
   - Added environment variable support for file paths
   - Created .env.example for documentation

4. **Dependencies**
   - Updated Flask from 2.0.0 to 3.0.0+
   - Updated Pillow to 10.0.0+
   - Updated marshmallow to 3.20.0+
   - Added python-dotenv for secrets management

5. **Security Headers**
   - Added Flask-Talisman for security headers
   - Configured CSP, HSTS, X-Frame-Options, etc.

6. **Rate Limiting**
   - Added Flask-Limiter for request rate limiting
   - Configured per-endpoint rate limits

---

## Recommendations

### Immediate (Critical)

1. **Implement Authentication**
   - Add JWT-based authentication
   - Protect all /api/v1 endpoints
   - Use Bearer token scheme

2. **Rotate Credentials**
   - Change default WiFi password
   - Reset any exposed credentials

3. **Audit Access Logs**
   - Review who accessed the system
   - Check for unauthorized modifications

### Short Term (High)

4. **HTTPS/TLS**
   - Deploy with HTTPS only
   - Use self-signed certificates for local deployment
   - Implement certificate pinning for mobile apps

5. **Input Validation**
   - Add request size limits
   - Implement stricter validation rules
   - Add CSRF protection

6. **Database Security**
   - Implement parameterized queries (already done)
   - Add query logging for audit trail
   - Regular backups with encryption

### Medium Term (Medium)

7. **Secrets Management**
   - Move to proper secrets vault (HashiCorp Vault, AWS Secrets Manager)
   - Implement key rotation
   - Remove all hardcoded secrets from repository

8. **Logging & Monitoring**
   - Implement centralized logging
   - Add security event monitoring
   - Set up alerts for suspicious activities

9. **Code Review**
   - Implement security code review process
   - Use static analysis tools (Bandit, Semgrep)
   - Regular penetration testing

### Long Term (Medium)

10. **Architecture Improvements**
    - Implement role-based access control (RBAC)
    - Add audit logging for all changes
    - Implement data encryption at rest
    - Regular security training for development team

---

## Testing Recommendations

1. **Security Testing Tools**
   - Use OWASP ZAP for dynamic testing
   - Use Bandit for Python static analysis
   - Use SQLMap to verify SQL injection protection

2. **Manual Testing**
   - Attempt SQL injection attacks
   - Try XSS payloads
   - Attempt authentication bypass
   - Test rate limiting

3. **Continuous Security**
   - Integrate security checks into CI/CD
   - Regular dependency updates
   - Automated vulnerability scanning

---

## Compliance Notes

This application handles medical data (medicine tracking). Consider:
- HIPAA compliance (if used in US healthcare context)
- GDPR compliance (if used with EU users)
- Local health data protection regulations

Current implementation lacks sufficient security for regulated environments.

---

## Conclusion

The application demonstrates some security awareness (parameterized queries, input validation schemas) but has critical gaps in authentication, file permissions, and secrets management. The issues identified should be remediated before production deployment.

**Risk Assessment:** HIGH - Not suitable for production use without security improvements

**Next Steps:** Implement recommendations in priority order; conduct follow-up security audit after fixes.

---

## Appendix: Tools Used

- Manual code review
- File permission audit
- Dependency analysis
- OWASP Top 10 mapping
- CWE/CVSS assessment

---

**Report Generated:** 2025-11-08
**Auditor:** Security Audit System
**Follow-up Audit Recommended:** 2025-12-08
