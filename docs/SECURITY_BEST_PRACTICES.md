# Security Best Practices Guide

## Overview

This guide documents security best practices implemented in the Pi Zero 2W Application Suite and standards for future development.

---

## Table of Contents

1. [Input Validation](#input-validation)
2. [SQL Injection Prevention](#sql-injection-prevention)
3. [XSS Prevention](#xss-prevention)
4. [Authentication & Authorization](#authentication--authorization)
5. [File Security](#file-security)
6. [Secrets Management](#secrets-management)
7. [Dependency Management](#dependency-management)
8. [Logging & Monitoring](#logging--monitoring)
9. [API Security](#api-security)
10. [Development Workflow](#development-workflow)

---

## Input Validation

### Best Practice #1: Always Validate Input

**Rule:** Never trust user input. Validate all data at entry points.

**Implementation:**

```python
# BAD - No validation
@api.route('/user/<username>')
def get_user(username):
    return db.query(f"SELECT * FROM users WHERE name = {username}")

# GOOD - With validation
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50)
    )

@api.route('/user/<username>')
def get_user(username):
    schema = UserSchema()
    data = schema.load({'username': username})
    return db.query("SELECT * FROM users WHERE name = ?", (data['username'],))
```

### Best Practice #2: Type Conversion with Bounds

**Rule:** Validate types and bounds for numeric parameters.

**Implementation:**

```python
# BAD - Integer overflow risk
page = int(request.args.get('page', 1))
per_page = int(request.args.get('per_page', 20))

# GOOD - With bounds checking
def get_pagination_params():
    page = max(1, int(request.args.get('page', 1)))
    per_page = int(request.args.get('per_page', 20))
    per_page = min(per_page, 100)  # Maximum 100 items
    per_page = max(per_page, 1)    # Minimum 1 item
    return page, per_page
```

### Best Practice #3: Date/Time Validation

**Rule:** Always validate date/time formats and handle parsing errors.

**Implementation:**

```python
# BAD - Unhandled exception
dt = datetime.strptime(user_input, "%Y-%m-%d")

# GOOD - With error handling
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

# In Flask endpoint
try:
    start_date = parse_date(request.args.get('start_date'))
except ValueError as e:
    return jsonify({'error': str(e)}), 400
```

### Best Practice #4: Whitelist Over Blacklist

**Rule:** Use allowlists (whitelist) validation instead of denylists.

**Implementation:**

```python
# BAD - Blacklist approach (incomplete)
allowed_time_windows = ['morning', 'afternoon', 'evening', 'night']
if 'invalid' not in user_input:
    process(user_input)

# GOOD - Whitelist approach
from marshmallow import validate

time_window = fields.Str(
    validate=validate.OneOf(['morning', 'afternoon', 'evening', 'night']),
    error='Invalid time window'
)
```

### Best Practice #5: String Sanitization

**Rule:** Sanitize strings by removing dangerous characters.

**Implementation:**

```python
def sanitize_string(value: str, max_length: int = 100) -> str:
    """Sanitize string input"""
    if not value:
        return ''

    # Remove control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char == '\n')

    # Limit length
    sanitized = sanitized[:max_length]

    # Strip whitespace
    return sanitized.strip()
```

---

## SQL Injection Prevention

### Best Practice #6: Always Use Parameterized Queries

**Rule:** Never concatenate user input into SQL strings. Always use parameters.

**Implementation:**

```python
# BAD - SQL injection vulnerable
medicine_id = request.args.get('id')
cursor.execute(f"SELECT * FROM medicines WHERE id = '{medicine_id}'")

# GOOD - Parameterized query
medicine_id = request.args.get('id')
cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))

# GOOD - Multiple parameters
cursor.execute("""
    SELECT * FROM medicines
    WHERE name = ? AND active = ?
""", (medicine_name, True))

# GOOD - List parameters
medicine_ids = ['med_1', 'med_2', 'med_3']
placeholders = ','.join(['?' for _ in medicine_ids])
cursor.execute(f"SELECT * FROM medicines WHERE id IN ({placeholders})", medicine_ids)
```

### Best Practice #7: ORM with Parameterization

**Rule:** Use ORMs that enforce parameterized queries (e.g., SQLAlchemy).

**Current Implementation:** Uses SQLite with explicit parameterized queries ✓

---

## XSS Prevention

### Best Practice #8: Output Encoding

**Rule:** Encode all output based on context (HTML, JSON, etc.).

**Implementation:**

```python
# BAD - Raw user input in response
message = request.args.get('message')
return f"<h1>{message}</h1>"

# GOOD - Using Flask with Jinja2 auto-escaping
@app.route('/')
def index():
    message = request.args.get('message', '')
    return render_template('template.html', message=message)

# In template.html - Jinja2 auto-escapes by default
<h1>{{ message }}</h1>

# For JSON responses - Flask handles escaping
return jsonify({'message': user_message})
```

### Best Practice #9: Content Security Policy

**Rule:** Implement strict CSP headers.

**Implementation:**

```python
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, force_https=True, strict_transport_security=True)
```

### Best Practice #10: Avoid innerHTML and eval()

**Rule:** Never use `eval()`, `exec()`, or set innerHTML with user data.

**Implementation:**

```python
# BAD - Never do this
user_code = request.args.get('code')
exec(user_code)

# BAD - Never do this
json_str = request.args.get('data')
data = eval(json_str)

# GOOD - Use json.loads() for JSON parsing
import json
json_str = request.args.get('data')
try:
    data = json.loads(json_str)
except json.JSONDecodeError:
    return jsonify({'error': 'Invalid JSON'}), 400
```

---

## Authentication & Authorization

### Best Practice #11: Implement Strong Authentication

**Rule:** Use JWT tokens or session-based authentication for all protected endpoints.

**Implementation:**

```python
from flask_jwt_extended import JWTManager, jwt_required

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

@api.route('/medicines', methods=['GET'])
@jwt_required()
def list_medicines():
    # Only authenticated users can access
    return get_medicines_data()
```

### Best Practice #12: Role-Based Access Control

**Rule:** Implement RBAC to control what authenticated users can do.

**Implementation:**

```python
from functools import wraps

def require_admin(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()
        user = User.query.get(identity)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@api.route('/medicines', methods=['DELETE'])
@require_admin
def delete_medicine():
    # Only admins can delete
    pass
```

### Best Practice #13: Secure Password Handling

**Rule:** Hash passwords with strong algorithms; never store plaintext.

**Implementation:**

```python
from werkzeug.security import generate_password_hash, check_password_hash

# When creating user
password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

# When authenticating
if check_password_hash(stored_hash, provided_password):
    # Authentication successful
    pass
```

---

## File Security

### Best Practice #14: Strict File Permissions

**Rule:** Use restrictive file permissions; only allow necessary access.

**Implementation:**

```bash
# Configuration files (sensitive data)
chmod 600 config.json
chmod 600 .env
chmod 700 /path/to/config/directory

# Backup files (sensitive data)
chmod 600 backups/*.json
chmod 700 backups/

# Database files
chmod 600 medicine.db
chmod 700 db/

# Source code (readable but not writable by others)
chmod 644 *.py
chmod 755 ./

# Executable scripts
chmod 755 /path/to/scripts/*.sh
```

### Best Practice #15: No World-Readable Secrets

**Rule:** Never make configuration or data files world-readable.

**Implementation:**

```python
import os
import stat

def secure_file(filepath, mode=0o600):
    """Set restrictive permissions on sensitive files"""
    if os.path.exists(filepath):
        os.chmod(filepath, mode)

        # Verify permissions
        file_stat = os.stat(filepath)
        file_mode = stat.filemode(file_stat.st_mode)

        if file_stat.st_mode & stat.S_IROTH:
            raise PermissionError(f"File {filepath} is readable by others!")
```

---

## Secrets Management

### Best Practice #16: Use Environment Variables

**Rule:** Never hardcode secrets; use environment variables.

**Implementation:**

```python
# BAD - Hardcoded secret
DATABASE_URL = "postgres://user:password@localhost/db"

# GOOD - Environment variable
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
```

### Best Practice #17: .env File Management

**Rule:** Create .env.example with placeholders; never commit .env file.

**Implementation:**

```bash
# .env.example (committed to repository)
DATABASE_URL=postgresql://user:password@localhost/dbname
JWT_SECRET_KEY=your-secret-key-here
API_KEY=your-api-key-here

# .env (gitignored, not committed)
DATABASE_URL=postgresql://user:actual-password@localhost/real-db
JWT_SECRET_KEY=<actual-secret-key>
API_KEY=<actual-api-key>
```

### Best Practice #18: Secret Rotation

**Rule:** Regularly rotate sensitive credentials.

**Implementation:**

```python
# Document secret rotation schedule
"""
Secret Rotation Schedule:
- JWT_SECRET_KEY: Every 90 days
- API Keys: Every 180 days
- Database passwords: Every 90 days
- WiFi passwords: Every 90 days
"""

# Implement key versioning
class SecretManager:
    def __init__(self):
        self.current_key = os.getenv('JWT_SECRET_KEY_V1')
        self.previous_keys = [
            os.getenv('JWT_SECRET_KEY_V0'),  # Old key, still valid for verification
        ]
```

---

## Dependency Management

### Best Practice #19: Keep Dependencies Updated

**Rule:** Regularly update dependencies to get security patches.

**Implementation:**

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade Flask

# Update all packages (with caution)
pip install -r requirements.txt --upgrade

# Use requirements.txt with pinned versions
Flask>=3.0.0,<4.0.0
Pillow>=10.0.0,<11.0.0
marshmallow>=3.20.0,<4.0.0
```

### Best Practice #20: Audit Dependencies for Vulnerabilities

**Rule:** Scan dependencies for known vulnerabilities.

**Implementation:**

```bash
# Using safety (checks PyPI vulnerability database)
pip install safety
safety check

# Using Bandit (Python security linter)
pip install bandit
bandit -r ./

# In requirements-dev.txt
safety>=2.3.0
bandit>=1.7.0
```

---

## Logging & Monitoring

### Best Practice #21: Structured Logging

**Rule:** Use structured logging for security events.

**Implementation:**

```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def log_auth_attempt(self, username, success, ip_address):
        """Log authentication attempt"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'AUTH_ATTEMPT',
            'username': username,
            'success': success,
            'ip_address': ip_address
        }
        self.logger.info(json.dumps(event))

    def log_unauthorized_access(self, user_id, resource, ip_address):
        """Log unauthorized access attempt"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'UNAUTHORIZED_ACCESS',
            'user_id': user_id,
            'resource': resource,
            'ip_address': ip_address,
            'severity': 'HIGH'
        }
        self.logger.warning(json.dumps(event))

security_logger = SecurityLogger(__name__)
```

### Best Practice #22: No Sensitive Data in Logs

**Rule:** Never log passwords, tokens, or PII.

**Implementation:**

```python
# BAD - Logs sensitive data
logger.info(f"User logged in with password: {password}")
logger.info(f"API token: {api_token}")

# GOOD - Only log non-sensitive information
logger.info(f"User authentication successful for user_id: {user_id}")
logger.info(f"API request from IP: {ip_address}")

# GOOD - Sanitize sensitive fields
def sanitize_log(data):
    """Remove sensitive fields from log data"""
    sensitive_fields = ['password', 'token', 'secret', 'key']
    sanitized = data.copy()
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'
    return sanitized
```

---

## API Security

### Best Practice #23: Use HTTPS/TLS Only

**Rule:** All API communication must use HTTPS.

**Implementation:**

```python
from flask_talisman import Talisman

app = Flask(__name__)

# Force HTTPS
Talisman(
    app,
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000  # 1 year
)
```

### Best Practice #24: Rate Limiting

**Rule:** Implement rate limiting to prevent abuse.

**Implementation:**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/medicines', methods=['GET'])
@limiter.limit("30 per minute")
def list_medicines():
    return get_medicines()
```

### Best Practice #25: Request/Response Validation

**Rule:** Validate all requests; limit response size.

**Implementation:**

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

@app.route('/api/medicines', methods=['POST'])
def create_medicine():
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 400

    if len(request.data) > 100000:  # 100KB limit
        return jsonify({'error': 'Request too large'}), 413

    # Validate with schema
    schema = MedicineSchema()
    data = schema.load(request.get_json())
    # Process...
```

### Best Practice #26: CORS Configuration

**Rule:** Configure CORS explicitly; avoid allowing all origins.

**Implementation:**

```python
from flask_cors import CORS

# BAD - Allows all origins
CORS(app)

# GOOD - Specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://trusted-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }
})
```

---

## Development Workflow

### Best Practice #27: Security Code Review

**Rule:** All code changes should undergo security review.

**Checklist for Reviewers:**
- [ ] Input validation present?
- [ ] Parameterized queries used?
- [ ] No hardcoded secrets?
- [ ] Proper error handling?
- [ ] Security headers set?
- [ ] Authentication/authorization enforced?
- [ ] Rate limiting applied?
- [ ] Logging appropriate (no sensitive data)?
- [ ] Dependencies updated?
- [ ] Tests cover security scenarios?

### Best Practice #28: Security Testing

**Rule:** Include security tests in your test suite.

**Implementation:**

```python
import unittest
from app import app

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_sql_injection_protection(self):
        """Verify SQL injection is prevented"""
        response = self.client.get("/api/medicines?id=' OR '1'='1")
        self.assertNotEqual(response.status_code, 200)

    def test_xss_protection(self):
        """Verify XSS is prevented"""
        response = self.client.post(
            "/api/medicines",
            json={'name': '<script>alert("XSS")</script>'}
        )
        self.assertEqual(response.status_code, 400)

    def test_authentication_required(self):
        """Verify endpoints require authentication"""
        response = self.client.get("/api/medicines")
        self.assertEqual(response.status_code, 401)
```

### Best Practice #29: Security Headers

**Rule:** Return security headers with all responses.

**Implementation:**

```python
# Using Flask-Talisman
from flask_talisman import Talisman

Talisman(
    app,
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self' 'unsafe-inline'",
    },
    x_content_type_options=True,
    x_frame_options='DENY',
    x_xss_protection=True
)
```

### Best Practice #30: Continuous Integration Security

**Rule:** Automate security checks in CI/CD pipeline.

**Implementation:**

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json

      - name: Check Dependencies
        run: |
          pip install safety
          safety check --json > safety-report.json

      - name: Run Tests
        run: pytest tests/ -v --cov=.
```

---

## Security Checklist for New Features

Before deploying new features, verify:

- [ ] Input validation implemented with schemas
- [ ] Parameterized queries used for all database access
- [ ] Output properly encoded (XSS prevention)
- [ ] Authentication/authorization enforced
- [ ] Rate limiting applied
- [ ] No hardcoded secrets
- [ ] File permissions appropriate
- [ ] Error handling doesn't leak information
- [ ] Security headers configured
- [ ] Logging appropriate (no PII/secrets)
- [ ] Dependencies up-to-date
- [ ] Security tests written
- [ ] Code reviewed for security
- [ ] Documentation updated

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Flask Security Documentation](https://flask.palletsprojects.com/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Next Review:** 2025-12-08
