# Pi Zero 2W Medicine Tracker API - Documentation

Welcome to the comprehensive API documentation for the Pi Zero 2W Medicine Tracker System. This folder contains all the documentation you need to understand, use, and integrate with the RESTful API.

## Quick Links

- **[API Quick Start](./API_QUICKSTART.md)** - Get started in 5 minutes
- **[Complete API Reference](./API_REFERENCE.md)** - All endpoints and parameters
- **[OpenAPI Specification](./openapi.yaml)** - Swagger/OpenAPI 3.0 format
- **[Error Codes](./ERROR_CODES.md)** - Understand and handle errors
- **[Authentication & Versioning](./API_AUTHENTICATION_VERSIONING.md)** - Security and version strategy

## Documentation Files

### 1. API_QUICKSTART.md
**Purpose:** Get up and running quickly with the API

**Contents:**
- Installation and setup
- Starting the API server
- Basic API usage examples
- Common use cases
- Testing with curl, Postman, Python, JavaScript
- Sample workflows

**Best For:** First-time users, quick integration examples

### 2. API_REFERENCE.md
**Purpose:** Complete technical reference for all endpoints

**Contents:**
- Response format specification
- All error codes and HTTP statuses
- Complete endpoint documentation
- Request/response examples
- Query parameters and headers
- Pagination details
- Date/time format specifications
- Common request patterns in multiple languages
- Best practices and troubleshooting

**Best For:** Integration development, endpoint details

### 3. openapi.yaml
**Purpose:** OpenAPI 3.0 specification for automated tools

**Contents:**
- Complete API schema in YAML format
- All endpoints with parameters
- Request/response schemas
- Error responses
- Data models
- Server configuration

**Best For:** Swagger UI, Postman import, code generation, API documentation tools

### 4. ERROR_CODES.md
**Purpose:** Understanding and handling API errors

**Contents:**
- Error response format
- All error codes with explanations
- HTTP status codes
- Common error scenarios
- Error handling examples in Python and JavaScript
- Troubleshooting guide
- Error logging patterns

**Best For:** Error handling, debugging, logging

### 5. API_AUTHENTICATION_VERSIONING.md
**Purpose:** Security, authentication, and versioning strategy

**Contents:**
- Current authentication status
- Planned authentication methods (API Key, JWT, OAuth)
- Security best practices
- API versioning strategy
- Backwards compatibility
- Migration guides
- Implementation roadmap

**Best For:** Security setup, planning upgrades, understanding versioning

## API Overview

### Base URL

```
Development:   http://localhost:5000/api/v1
Production:    http://{hostname}:5000/api/v1
```

### Current Version

- **Version:** 1.0.0
- **Status:** Stable
- **Authentication:** None (Development)
- **Rate Limiting:** Disabled (Development)

### Key Features

**Medicines Management**
- CRUD operations (Create, Read, Update, Delete)
- Pending medicines (due now)
- Low stock alerts
- Mark medicines as taken (single or batch)

**Tracking & Adherence**
- Medicine tracking history
- Today's adherence statistics
- Adherence statistics over periods
- Daily breakdown

**Configuration Management**
- Get/update application settings
- Multiple configuration sections
- Atomic updates

## Quick Start

### 1. Start the API Server

```bash
cd /home/user/pizerowgpio
python3 run_api.py
```

### 2. Test the API

```bash
# Check health
curl http://localhost:5000/api/v1/health

# Create a medicine
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Daily",
    "stock": 100
  }'

# List medicines
curl http://localhost:5000/api/v1/medicines

# Get today's stats
curl http://localhost:5000/api/v1/tracking/today
```

### 3. Explore the API

- Visit [API Quick Start](./API_QUICKSTART.md) for detailed examples
- Check [API Reference](./API_REFERENCE.md) for complete endpoint list
- Import [openapi.yaml](./openapi.yaml) into Postman or Swagger UI

## API Endpoints Summary

### Health & Info
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Documentation links

### Medicines
- `GET /medicines` - List medicines
- `POST /medicines` - Create medicine
- `GET /medicines/{id}` - Get medicine
- `PUT /medicines/{id}` - Update medicine
- `PATCH /medicines/{id}` - Partial update
- `DELETE /medicines/{id}` - Delete medicine
- `GET /medicines/pending` - Pending medicines
- `GET /medicines/low-stock` - Low stock medicines
- `POST /medicines/{id}/take` - Mark taken
- `POST /medicines/batch-take` - Batch mark taken

### Tracking
- `GET /medicines/{id}/tracking` - Medicine history
- `GET /tracking` - All tracking
- `POST /tracking` - Batch mark taken
- `GET /tracking/today` - Today's stats
- `GET /tracking/stats` - Adherence statistics

### Configuration
- `GET /config` - Get all config
- `PUT /config` - Update all config
- `GET /config/{section}` - Get section
- `PUT /config/{section}` - Update section
- `PATCH /config/{section}` - Partial update

## Documentation Structure

```
docs/
├── README.md                           # This file
├── API_QUICKSTART.md                   # Getting started guide
├── API_REFERENCE.md                    # Complete endpoint reference
├── openapi.yaml                        # OpenAPI 3.0 specification
├── ERROR_CODES.md                      # Error code reference
└── API_AUTHENTICATION_VERSIONING.md    # Security and versioning
```

## Response Format

All responses follow this format:

### Success
```json
{
  "success": true,
  "message": "Optional message",
  "data": { /* response data */ },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { /* additional info */ }
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

## Common Parameters

### Pagination
- `page` (default: 1) - Page number
- `per_page` (default: 20, max: 100) - Items per page

### Filtering
- `start_date` (YYYY-MM-DD) - Start date
- `end_date` (YYYY-MM-DD) - End date
- `active` (true/false) - Filter by active status

### Sorting
- `sort` (string) - Field to sort by
- `order` (asc/desc) - Sort order

## HTTP Methods

| Method | Purpose |
|--------|---------|
| GET | Retrieve data |
| POST | Create new resource or bulk operation |
| PUT | Replace entire resource |
| PATCH | Update partial resource |
| DELETE | Remove resource |

## Common Use Cases

### Daily Routine
1. Check pending medicines: `GET /medicines/pending`
2. Mark morning medicines: `POST /medicines/batch-take`
3. Check adherence: `GET /tracking/today`

### Medication Management
1. Add new medicine: `POST /medicines`
2. Update stock: `PATCH /medicines/{id}`
3. Check low stock: `GET /medicines/low-stock`

### Reporting
1. Get weekly stats: `GET /tracking/stats?start_date=...&end_date=...`
2. Get medicine history: `GET /medicines/{id}/tracking`
3. Export data for analysis

## Tools & Integration

### For Testing
- **cURL** - Command line tool (built-in)
- **Postman** - GUI tool (import openapi.yaml)
- **Swagger UI** - Web-based explorer
- **Thunder Client** - VS Code extension

### For Integration
- **Python** - requests library
- **JavaScript** - fetch API
- **Java** - OkHttp, HttpClient
- **Go** - net/http
- **iOS** - URLSession
- **Android** - HttpURLConnection, OkHttp

## Development

### Project Structure

```
/home/user/pizerowgpio/
├── api/                      # API implementation
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration
│   └── v1/                  # API v1
│       ├── routes/          # Endpoint handlers
│       ├── serializers/     # Response formatters
│       ├── middleware/      # Custom middleware
│       └── services/        # Business logic
├── db/                      # Database layer
├── docs/                    # Documentation (this folder)
├── tests/                   # Test suite
├── run_api.py              # API server entry point
├── requirements.txt        # Python dependencies
└── config.json            # Application config
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/

# With coverage
pytest --cov=api tests/
```

### Environment Setup

```bash
# Development
export FLASK_ENV=development
export FLASK_DEBUG=True
export FLASK_PORT=5000

# Production
export FLASK_ENV=production
export FLASK_DEBUG=False
export SECRET_KEY=your-secret-key
```

## Support & Resources

### Documentation
- [API Quick Start](./API_QUICKSTART.md) - Getting started
- [API Reference](./API_REFERENCE.md) - Complete endpoint guide
- [Error Codes](./ERROR_CODES.md) - Error handling

### Files
- [openapi.yaml](./openapi.yaml) - API specification
- [API_DESIGN.md](./API_DESIGN.md) - Architecture details (if available)
- [API_ENDPOINT_INVENTORY.md](./API_ENDPOINT_INVENTORY.md) - Endpoint listing (if available)

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.0.3)
- [REST API Best Practices](https://restfulapi.net/)

## Changelog

### Version 1.0.0 (November 2025)
- Initial API release
- Medicine management endpoints
- Tracking and adherence endpoints
- Configuration management endpoints
- OpenAPI 3.0 specification
- Comprehensive documentation

### Planned for v1.1
- API Key authentication
- Enhanced validation
- Rate limiting
- Audit logging

### Planned for v1.2
- JWT authentication
- User/role management
- Advanced statistics
- Data export/import

## Support

For issues or questions:

1. Check the appropriate documentation:
   - Installation issues → [API_QUICKSTART.md](./API_QUICKSTART.md)
   - Endpoint details → [API_REFERENCE.md](./API_REFERENCE.md)
   - Error handling → [ERROR_CODES.md](./ERROR_CODES.md)

2. Enable debug mode:
   ```bash
   export FLASK_DEBUG=True
   python3 run_api.py
   ```

3. Check server logs for detailed error messages

4. Verify API is running:
   ```bash
   curl http://localhost:5000/api/v1/health
   ```

## License

This API documentation is part of the Pi Zero 2W Medicine Tracker System. See LICENSE file for details.

---

## Next Steps

- **New to the API?** Start with [API_QUICKSTART.md](./API_QUICKSTART.md)
- **Need endpoint details?** See [API_REFERENCE.md](./API_REFERENCE.md)
- **Setting up production?** Review [API_AUTHENTICATION_VERSIONING.md](./API_AUTHENTICATION_VERSIONING.md)
- **Handling errors?** Check [ERROR_CODES.md](./ERROR_CODES.md)
- **Using with tools?** Import [openapi.yaml](./openapi.yaml)

Happy coding!
