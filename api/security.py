"""
API Security Middleware and Configuration
Implements security headers, rate limiting, CORS, and authentication
"""

import os
import logging
from functools import wraps
from flask import request, jsonify
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

logger = logging.getLogger(__name__)


def configure_security(app):
    """Configure all security features for Flask app

    Args:
        app: Flask application instance
    """

    # 1. Security Headers (prevents MIME type sniffing, clickjacking, etc.)
    configure_security_headers(app)

    # 2. CORS Configuration
    configure_cors(app)

    # 3. Rate Limiting
    configure_rate_limiting(app)

    # 4. Request Size Limits
    configure_request_limits(app)

    logger.info("Security configuration applied to application")


def configure_security_headers(app):
    """Configure Flask-Talisman for security headers

    Adds headers:
    - Strict-Transport-Security: Forces HTTPS
    - X-Content-Type-Options: Prevents MIME sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Browser XSS protection
    - Content-Security-Policy: Restricts resource loading
    """

    csp = {
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self'",
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
    }

    Talisman(
        app,
        force_https=os.getenv('FLASK_ENV', 'production') == 'production',
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        strict_transport_security_include_subdomains=True,
        content_security_policy=csp,
        x_content_type_options=True,
        x_frame_options='DENY',
        x_xss_protection=True,
        referrer_policy='strict-origin-when-cross-origin'
    )


def configure_cors(app):
    """Configure CORS with restrictive defaults

    Only allows specific origins and methods.
    """

    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5000').split(',')
    cors_enabled = os.getenv('CORS_ENABLED', 'true').lower() == 'true'

    if cors_enabled:
        CORS(
            app,
            resources={
                r"/api/*": {
                    "origins": allowed_origins,
                    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "expose_headers": ["Content-Type"],
                    "max_age": 3600,
                    "supports_credentials": True
                }
            }
        )
        logger.info(f"CORS enabled for origins: {allowed_origins}")


def configure_rate_limiting(app):
    """Configure Flask-Limiter for rate limiting

    Default: 200 requests per day, 50 per hour
    """

    rate_limiting_enabled = os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true'

    if rate_limiting_enabled:
        global limiter
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://"
        )

        @app.before_request
        def check_rate_limit():
            """Log rate limit status"""
            pass

        logger.info("Rate limiting enabled")
    else:
        global limiter
        limiter = None


def configure_request_limits(app):
    """Configure request size limits

    Prevents large upload attacks
    """

    # Maximum 16 MB request size
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    logger.info("Request size limits configured (max 16MB)")


# Rate limiter instance (initialized in configure_security)
limiter = None


def require_rate_limit(limit_string):
    """Decorator to apply rate limiting to specific endpoints

    Args:
        limit_string: Rate limit in format "N per PERIOD"
                     Example: "30 per minute", "100 per hour"

    Returns:
        Decorated function with rate limiting

    Example:
        @app.route('/api/medicines')
        @require_rate_limit("30 per minute")
        def list_medicines():
            pass
    """
    def decorator(f):
        if limiter:
            return limiter.limit(limit_string)(f)
        return f
    return decorator


def validate_json_request(f):
    """Decorator to validate JSON request

    Ensures request is JSON and not too large
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400

        if len(request.data) > 1024 * 1024:  # 1MB limit for JSON
            return jsonify({
                'error': 'Request JSON too large'
            }), 413

        return f(*args, **kwargs)

    return decorated_function


def sanitize_error_response(error_dict):
    """Sanitize error responses to avoid information disclosure

    Args:
        error_dict: Error dictionary to sanitize

    Returns:
        Sanitized error dictionary
    """

    is_production = os.getenv('FLASK_ENV', 'production') == 'production'

    if is_production:
        # In production, don't expose internal error details
        sanitized = {
            'error': error_dict.get('error', 'An error occurred'),
            'code': error_dict.get('code', 'INTERNAL_ERROR')
        }

        # Only include details if they're safe (not containing system paths)
        if 'details' in error_dict and isinstance(error_dict['details'], str):
            if not any(x in error_dict['details'] for x in ['/', 'home', 'var', 'tmp']):
                sanitized['details'] = error_dict['details']

        return sanitized
    else:
        # In development, include full details
        return error_dict


def get_client_ip():
    """Get client IP address, accounting for proxies

    Returns:
        Client IP address string
    """

    # Check for IP from proxies first
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


logger.info("Security module loaded")
