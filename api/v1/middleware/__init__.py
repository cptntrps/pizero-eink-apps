"""
API v1 Middleware Package

This package contains middleware for request/response processing:
- Input validation
- Error handling
- Request logging
- Authentication (future)
- Rate limiting (future)
"""

# Import middleware modules
from . import errors
from . import logging_middleware

# Export main components
from .errors import (
    APIError,
    ValidationError,
    ResourceNotFoundError,
    DuplicateResourceError,
    DatabaseError,
    register_error_handlers,
    with_error_handling
)

from .logging_middleware import (
    RequestLogger,
    log_route,
    log_slow_requests,
    log_database_queries,
    performance_monitor
)

__all__ = [
    'errors',
    'logging_middleware',
    'APIError',
    'ValidationError',
    'ResourceNotFoundError',
    'DuplicateResourceError',
    'DatabaseError',
    'register_error_handlers',
    'with_error_handling',
    'RequestLogger',
    'log_route',
    'log_slow_requests',
    'log_database_queries',
    'performance_monitor'
]
