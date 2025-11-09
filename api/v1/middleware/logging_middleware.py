"""
Request Logging Middleware
Comprehensive request/response logging for API v1

This module logs all API requests, responses, and errors with detailed
context including timing, status codes, and request parameters.
"""

import logging
import time
import json
from datetime import datetime
from flask import request, g
from functools import wraps

logger = logging.getLogger(__name__)


class RequestLogger:
    """Request logger with timing and context tracking"""

    def __init__(self, app=None):
        """
        Initialize request logger

        Args:
            app: Flask application instance (optional)
        """
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize logging middleware with Flask app

        Args:
            app: Flask application instance
        """
        # Register before_request handler
        app.before_request(self.before_request)

        # Register after_request handler
        app.after_request(self.after_request)

        # Register teardown handler
        app.teardown_request(self.teardown_request)

        logger.info("Request logging middleware initialized")

    @staticmethod
    def before_request():
        """
        Called before each request
        Records request start time and logs request details
        """
        # Record start time
        g.request_start_time = time.time()

        # Generate request ID
        g.request_id = f"req_{int(time.time() * 1000)}"

        # Log request details
        request_info = {
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'timestamp': datetime.now().isoformat()
        }

        # Log query parameters (if any)
        if request.args:
            request_info['query_params'] = dict(request.args)

        # Log request body for POST/PUT/PATCH (be careful with sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.is_json:
                    body = request.get_json()
                    # Redact sensitive fields
                    sanitized_body = sanitize_request_body(body)
                    request_info['body'] = sanitized_body
                else:
                    request_info['body_type'] = request.content_type
            except Exception as e:
                logger.warning(f"Failed to parse request body: {e}")

        logger.info(f"Request started: {json.dumps(request_info)}")

    @staticmethod
    def after_request(response):
        """
        Called after each request
        Logs response details and timing

        Args:
            response: Flask response object

        Returns:
            Response object (unchanged)
        """
        # Calculate request duration
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            duration_ms = round(duration * 1000, 2)
        else:
            duration_ms = None

        # Log response details
        response_info = {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': duration_ms,
            'content_length': response.content_length,
            'timestamp': datetime.now().isoformat()
        }

        # Add timing header to response
        if duration_ms:
            response.headers['X-Request-Duration-Ms'] = str(duration_ms)

        # Add request ID header
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id

        # Log based on status code
        if response.status_code >= 500:
            logger.error(f"Request failed: {json.dumps(response_info)}")
        elif response.status_code >= 400:
            logger.warning(f"Request error: {json.dumps(response_info)}")
        else:
            logger.info(f"Request completed: {json.dumps(response_info)}")

        return response

    @staticmethod
    def teardown_request(exception=None):
        """
        Called when request context is torn down
        Logs any exceptions that occurred

        Args:
            exception: Exception instance (if any)
        """
        if exception:
            error_info = {
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'timestamp': datetime.now().isoformat()
            }

            logger.error(f"Request exception: {json.dumps(error_info)}", exc_info=True)


def sanitize_request_body(body):
    """
    Sanitize request body to remove sensitive information

    Args:
        body: Request body (dict or other)

    Returns:
        Sanitized body
    """
    if not isinstance(body, dict):
        return body

    # List of sensitive field names to redact
    sensitive_fields = [
        'password', 'token', 'secret', 'api_key', 'auth',
        'wifi_password', 'hotspot_password'
    ]

    sanitized = {}
    for key, value in body.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_body(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_request_body(item) if isinstance(item, dict) else item
                             for item in value]
        else:
            sanitized[key] = value

    return sanitized


def log_route(func):
    """
    Decorator to add detailed logging to specific routes

    Usage:
        @api_v1_bp.route('/example')
        @log_route
        def example_route():
            # Your code here
            pass

    Args:
        func: Route function to wrap

    Returns:
        Wrapped function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        logger.info(f"Entering route: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.info(f"Route {func.__name__} completed in {duration_ms}ms")
            return result
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Route {func.__name__} failed after {duration_ms}ms: {e}")
            raise

    return wrapper


def log_slow_requests(threshold_ms=1000):
    """
    Decorator to log slow requests (requests exceeding threshold)

    Usage:
        @api_v1_bp.route('/example')
        @log_slow_requests(threshold_ms=500)
        def example_route():
            # Your code here
            pass

    Args:
        threshold_ms: Threshold in milliseconds

    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            if duration_ms > threshold_ms:
                logger.warning(f"Slow request: {func.__name__} took {duration_ms}ms "
                             f"(threshold: {threshold_ms}ms)")

            return result

        return wrapper
    return decorator


def log_database_queries(func):
    """
    Decorator to log database operations

    Usage:
        @log_database_queries
        def get_medicines():
            # Your database code here
            pass

    Args:
        func: Database function to wrap

    Returns:
        Wrapped function with logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        logger.debug(f"Database operation: {func.__name__}")

        try:
            result = func(*args, **kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)

            logger.debug(f"Database operation {func.__name__} completed in {duration_ms}ms")

            # Log slow database queries (> 100ms)
            if duration_ms > 100:
                logger.warning(f"Slow database query: {func.__name__} took {duration_ms}ms")

            return result
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Database operation {func.__name__} failed after {duration_ms}ms: {e}")
            raise

    return wrapper


class PerformanceMonitor:
    """Monitor and log API performance metrics"""

    def __init__(self):
        self.request_times = []
        self.endpoint_stats = {}

    def record_request(self, endpoint, duration_ms, status_code):
        """
        Record request metrics

        Args:
            endpoint: Endpoint path
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
        """
        self.request_times.append(duration_ms)

        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                'total_requests': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'errors': 0
            }

        stats = self.endpoint_stats[endpoint]
        stats['total_requests'] += 1
        stats['total_time'] += duration_ms
        stats['min_time'] = min(stats['min_time'], duration_ms)
        stats['max_time'] = max(stats['max_time'], duration_ms)

        if status_code >= 400:
            stats['errors'] += 1

    def get_stats(self):
        """
        Get performance statistics

        Returns:
            Dictionary with performance metrics
        """
        if not self.request_times:
            return {}

        return {
            'total_requests': len(self.request_times),
            'average_time_ms': sum(self.request_times) / len(self.request_times),
            'min_time_ms': min(self.request_times),
            'max_time_ms': max(self.request_times),
            'endpoint_stats': self.endpoint_stats
        }

    def log_stats(self):
        """Log current performance statistics"""
        stats = self.get_stats()
        if stats:
            logger.info(f"Performance stats: {json.dumps(stats, indent=2)}")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


logger.info("Logging middleware module loaded")
