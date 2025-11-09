# API Authentication & Versioning Strategy

## Table of Contents

1. [Authentication Overview](#authentication-overview)
2. [Current Authentication Status](#current-authentication-status)
3. [Planned Authentication Methods](#planned-authentication-methods)
4. [Security Best Practices](#security-best-practices)
5. [API Versioning Strategy](#api-versioning-strategy)
6. [Backwards Compatibility](#backwards-compatibility)
7. [Migration Guide](#migration-guide)

---

## Authentication Overview

### Current Status: No Authentication (Development)

The API currently operates **without authentication** in development mode. This is suitable for:
- Local development and testing
- Protected network environments
- Internal use on Pi Zero devices

**WARNING:** Do not expose the API to untrusted networks without authentication.

### Security Responsibility

When deploying to production or untrusted networks, implement one of the planned authentication methods detailed below.

---

## Current Authentication Status

### Development Mode

```
API_VERSION: 1.0.0
AUTHENTICATION: None (Development)
CORS: Enabled (all origins)
RATE_LIMITING: Disabled
```

### Access Pattern

```bash
# No authentication headers required
curl http://localhost:5000/api/v1/medicines
```

### Environment Configuration

```python
# From api/config.py
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    CORS_ENABLED = True
    RATE_LIMIT_ENABLED = False
```

---

## Planned Authentication Methods

### 1. API Key Authentication

**Status:** Planned for v1.1

**Implementation:**

Clients will include an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" \
  http://localhost:5000/api/v1/medicines
```

**Key Management:**

- Keys stored in database or configuration file
- Per-client/app key tracking
- Key rotation mechanism
- Rate limiting per key

**Security Features:**

- HTTPS required in production
- Keys stored as hashed values
- Audit logging of key usage
- Automatic key expiration

**Configuration:**

```python
# Planned configuration
class ProductionConfig(BaseConfig):
    AUTH_ENABLED = True
    AUTH_METHOD = 'api_key'
    RATE_LIMIT_ENABLED = True
    REQUIRE_HTTPS = True
```

**Example Usage:**

```python
import requests

headers = {
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json'
}

response = requests.get(
    'http://localhost:5000/api/v1/medicines',
    headers=headers
)
```

### 2. JWT (JSON Web Token) Authentication

**Status:** Planned for v1.2

**Implementation:**

Client obtains a token and includes it in the `Authorization` header:

```bash
# 1. Get token
curl -X POST http://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Response:
# {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "expires_in": 3600
# }

# 2. Use token in requests
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://localhost:5000/api/v1/medicines
```

**Benefits:**

- Stateless authentication
- Token expiration
- User/role-based access control
- Refresh token mechanism
- Cross-origin friendly

**Planned Endpoints:**

```
POST /auth/login          - Authenticate user
POST /auth/token          - Get JWT token
POST /auth/refresh        - Refresh token
POST /auth/logout         - Revoke token
GET  /auth/me             - Get current user info
```

**Security Features:**

- RS256 or HS256 signing
- Token expiration (default: 1 hour)
- Refresh tokens (24 hours)
- HTTPS required
- Token blacklist for revoked tokens

### 3. OAuth 2.0 (Future Enhancement)

**Status:** Planned for v2.0

**Supports:**

- Third-party integrations
- Mobile app authentication
- Social login (Google, Apple)
- Delegated access

---

## Security Best Practices

### Current (Development)

1. **Network Isolation**
   - Run API only on private networks
   - Use firewall rules to restrict access
   - Don't expose to the internet

2. **HTTPS/SSL**
   - Use HTTPS in any production-like environment
   - Self-signed certificates acceptable for internal use
   - Certificate pinning for critical clients

3. **CORS Configuration**
   - Restrict CORS origins in production
   - Only allow trusted domains
   - Disable CORS if not needed

   ```python
   # Restrict CORS
   CORS(app, resources={
       r"/api/*": {
           "origins": ["https://trusted-domain.com"],
           "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
           "allow_headers": ["Content-Type"]
       }
   })
   ```

4. **Rate Limiting**
   - Enable rate limiting in production
   - Limit requests per IP or API key
   - Implement exponential backoff

5. **Logging & Monitoring**
   - Log all API requests
   - Monitor for suspicious activity
   - Alert on errors and failures

### When Implementing Authentication

1. **Store Credentials Securely**
   - Hash passwords with bcrypt or argon2
   - Never log authentication credentials
   - Rotate secrets regularly

2. **Transport Security**
   - Enforce HTTPS/TLS 1.2+
   - Use strong ciphers
   - Enable HSTS headers

3. **Token/Key Management**
   - Short expiration times
   - Secure token storage on clients
   - Implement token refresh mechanism
   - Audit token usage

4. **Request Validation**
   - Validate all input
   - Sanitize data
   - Implement input size limits
   - Check for injection attacks

5. **Response Security**
   - Don't expose sensitive information in errors
   - Set security headers:
     ```
     X-Content-Type-Options: nosniff
     X-Frame-Options: DENY
     X-XSS-Protection: 1; mode=block
     Strict-Transport-Security: max-age=31536000
     ```

---

## API Versioning Strategy

### URI Versioning

The API uses URI-based versioning for explicit version control.

**Format:** `/api/v{major}/endpoint`

```
/api/v1/medicines       - Version 1.0
/api/v2/medicines       - Version 2.0 (future)
/api/v3/medicines       - Version 3.0 (future)
```

### Version Identification

**In Response Headers:**

```
X-API-Version: 1.0.0
API-Version: 1.0
```

**In Response Body:**

```json
{
  "success": true,
  "meta": {
    "api_version": "1.0.0",
    "timestamp": "2025-11-08T15:30:00"
  }
}
```

### Version Lifecycle

**Version 1.0.0** (Current)
- Status: Active/Stable
- Release Date: November 2025
- Support Duration: 24 months
- End of Life: November 2027

**Version 2.0** (Planned)
- Status: In Planning
- Estimated Release: 2026
- Expected Features: JWT auth, enhanced validation, new endpoints
- Migration Path: v1 support continues for 12 months

**Version 3.0** (Future)
- Status: Conceptual
- Planned Features: OAuth 2.0, webhook support, GraphQL API

### Deprecation Policy

**Deprecation Timeline:**

1. **Announcement** - 6 months notice
   - Announce in API documentation
   - Email to API consumers
   - Deprecation headers in responses

2. **Deprecation Period** - 12 months
   - Old version continues to work
   - Deprecation warnings in responses
   - Migration guides provided
   - Technical support available

3. **End of Life** - Version discontinued
   - Old endpoints return 410 Gone
   - No further updates or support

**Deprecation Header Example:**

```
Deprecation: true
Sunset: Sun, 30 Nov 2027 00:00:00 UTC
Warning: 299 - "API endpoint is deprecated, use /api/v2/... instead"
```

### Feature Versioning

**Within a version, features may have different stability levels:**

| Level | Status | Support |
|-------|--------|---------|
| Stable | Production ready | Full support |
| Beta | Pre-release | Limited support |
| Experimental | Proof of concept | No SLA |
| Deprecated | Will be removed | Limited support |

**Feature Status in Response:**

```json
{
  "features": {
    "medicines": {
      "status": "stable",
      "version": "1.0"
    },
    "tracking": {
      "status": "stable",
      "version": "1.0"
    },
    "config": {
      "status": "stable",
      "version": "1.0"
    },
    "batch_operations": {
      "status": "beta",
      "version": "1.1"
    }
  }
}
```

---

## Backwards Compatibility

### Compatibility Guarantee

Within a major version (e.g., v1.x), the API maintains backwards compatibility:

- **Response formats** don't change
- **Required parameters** don't change
- **HTTP status codes** don't change (unless correcting bugs)
- **Endpoint paths** don't change

### Safe Changes

Changes that don't break backwards compatibility:

- Adding optional parameters
- Adding new optional fields to responses
- Adding new endpoints
- Extending error messages
- Changing implementation details (not observable)

### Breaking Changes

Changes that break backwards compatibility:

- Removing endpoints
- Changing parameter types
- Removing response fields
- Changing required fields
- Changing error codes
- Changing behavior of endpoints

### Handling Breaking Changes

Breaking changes only occur in major version updates (v1 → v2):

1. Announce 6 months in advance
2. Provide migration guide
3. Support both versions for 12 months
4. Sunset old version with 6 months notice

### Response Evolution Example

**v1.0 Response:**
```json
{
  "success": true,
  "data": {
    "id": "med_123",
    "name": "Aspirin"
  }
}
```

**v1.1 Response (backwards compatible):**
```json
{
  "success": true,
  "data": {
    "id": "med_123",
    "name": "Aspirin",
    "dosage": "500mg"  // New optional field
  }
}
```

**v2.0 Response (breaking change):**
```json
{
  "success": true,
  "data": {
    "id": "med_123",
    "name": "Aspirin",
    "strength": "500mg",  // Renamed from dosage
    "metadata": {         // New structure
      "created": "2025-11-08T15:30:00"
    }
  }
}
```

---

## Migration Guide

### Migrating from No Auth to API Key Auth

**Step 1: Add API Key Header**

Before:
```python
import requests
response = requests.get('http://localhost:5000/api/v1/medicines')
```

After:
```python
import requests

headers = {'X-API-Key': 'your-api-key-here'}
response = requests.get(
    'http://localhost:5000/api/v1/medicines',
    headers=headers
)
```

**Step 2: Store Keys Securely**

```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

headers = {'X-API-Key': API_KEY}
```

### Migrating from No Auth to JWT

**Step 1: Obtain Token**

```python
import requests
import json

# Authenticate
response = requests.post(
    'http://localhost:5000/api/auth/token',
    json={'username': 'user', 'password': 'password'}
)
token = response.json()['token']
```

**Step 2: Use Token in Requests**

```python
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:5000/api/v1/medicines',
    headers=headers
)
```

**Step 3: Handle Token Expiration**

```python
import requests
from requests.auth import AuthBase

class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

class APISession:
    def __init__(self, username, password, base_url):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.token = None
        self.refresh_token = None
        self.refresh_token_expiry = None

    def login(self):
        response = requests.post(
            f'{self.base_url}/api/auth/token',
            json={'username': self.username, 'password': self.password}
        )
        data = response.json()
        self.token = data['token']
        self.refresh_token = data.get('refresh_token')

    def get(self, endpoint, **kwargs):
        if not self.token:
            self.login()

        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.token}'

        response = requests.get(
            f'{self.base_url}{endpoint}',
            headers=headers,
            **kwargs
        )

        if response.status_code == 401:
            self.login()
            headers['Authorization'] = f'Bearer {self.token}'
            response = requests.get(
                f'{self.base_url}{endpoint}',
                headers=headers,
                **kwargs
            )

        return response

# Usage
session = APISession('user', 'password', 'http://localhost:5000/api/v1')
response = session.get('/medicines')
```

### Migrating from v1 to v2

**Step 1: Identify Breaking Changes**

Check release notes for breaking changes between versions.

**Step 2: Update Endpoint Paths**

Before:
```python
response = requests.get('http://localhost:5000/api/v1/medicines')
```

After:
```python
response = requests.get('http://localhost:5000/api/v2/medicines')
```

**Step 3: Update Response Handling**

Check if response structure changed and update parsing code.

**Step 4: Test Thoroughly**

Test with both v1 and v2 endpoints during migration period.

**Step 5: Full Migration**

Once comfortable, remove v1 code and switch entirely to v2.

---

## Implementation Roadmap

### v1.0 (Current - November 2025)
- No authentication
- URI versioning
- REST API
- Medicine management
- Tracking and statistics
- Configuration management

### v1.1 (Q2 2026)
- API Key authentication
- Enhanced validation
- Batch operations optimization
- Rate limiting
- Audit logging

### v1.2 (Q4 2026)
- JWT authentication
- User/role management
- Advanced statistics
- Data export/import
- Webhook support (experimental)

### v2.0 (2026)
- OAuth 2.0 support
- GraphQL API (experimental)
- Enhanced security
- Performance improvements
- Mobile-optimized endpoints

---

## FAQ

**Q: When will authentication be required?**
A: Not in v1.0. Planned for v1.1. Will be optional initially, required in production in v1.2.

**Q: Can I run v1 and v2 endpoints simultaneously?**
A: Yes, during migration periods. Both versions can coexist for 12 months.

**Q: How do I get an API key?**
A: Not implemented yet. Coming in v1.1. Will be available through configuration or admin panel.

**Q: What happens to my scripts if authentication is added?**
A: You'll need to add auth headers. We'll provide migration guides and maintain backwards compatibility as much as possible.

**Q: Is HTTPS required?**
A: Not in development. Strongly recommended in production, required with authentication.

**Q: Can I request a feature?**
A: Yes! Use the issue tracker or contact the development team.

---

## Security Checklist

Before deploying to production:

- [ ] Enable authentication (API Key or JWT)
- [ ] Configure HTTPS/TLS
- [ ] Set strong SECRET_KEY
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Enable logging and monitoring
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Test error handling
- [ ] Document API access controls

---

## Support & Contact

For authentication and versioning questions:
- Check this documentation
- Review API_REFERENCE.md
- Check code comments in api/ directory
- Open an issue on the project repository
