"""
Error Handling Middleware
Provides comprehensive error handling for the API v1

This module centralizes error handling logic, ensuring consistent error
responses across all endpoints and proper logging of errors.
"""

import logging
import sqlite3
from datetime import datetime
from functools import wraps
from flask import jsonify, request

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors"""

    def __init__(self, message, code='INTERNAL_ERROR', status_code=500, details=None):
        """
        Initialize API error

        Args:
            message: Error message
            code: Error code (string)
            status_code: HTTP status code
            details: Additional error details (dict or string)
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ValidationError(APIError):
    """Validation error (400 Bad Request)"""

    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='VALIDATION_ERROR',
            status_code=400,
            details=details
        )


class ResourceNotFoundError(APIError):
    """Resource not found error (404 Not Found)"""

    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='RESOURCE_NOT_FOUND',
            status_code=404,
            details=details
        )


class DuplicateResourceError(APIError):
    """Duplicate resource error (409 Conflict)"""

    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='DUPLICATE_RESOURCE',
            status_code=409,
            details=details
        )


class DatabaseError(APIError):
    """Database operation error (500 Internal Server Error)"""

    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='DATABASE_ERROR',
            status_code=500,
            details=details
        )


def create_error_response(code, message, details=None, status_code=400):
    """
    Create standardized error response

    Args:
        code: Error code (string)
        message: Error message
        details: Additional error details
        status_code: HTTP status code

    Returns:
        Tuple of (response dict, status code)
    """
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        },
        'meta': {
            'timestamp': datetime.now().isoformat()
        }
    }

    if details:
        response['error']['details'] = details

    return response, status_code


def handle_api_error(error):
    """
    Handle APIError exceptions

    Args:
        error: APIError instance

    Returns:
        JSON error response
    """
    logger.error(f"API Error: {error.code} - {error.message}")

    return jsonify(create_error_response(
        code=error.code,
        message=error.message,
        details=error.details,
        status_code=error.status_code
    )[0]), error.status_code


def handle_marshmallow_validation_error(error):
    """
    Handle Marshmallow ValidationError

    Args:
        error: ValidationError instance

    Returns:
        JSON error response
    """
    logger.warning(f"Validation error: {error.messages}")

    return jsonify(create_error_response(
        code='VALIDATION_ERROR',
        message='Validation failed',
        details=error.messages,
        status_code=400
    )[0]), 400


def handle_database_error(error):
    """
    Handle database errors (sqlite3 errors)

    Args:
        error: Database exception

    Returns:
        JSON error response
    """
    logger.error(f"Database error: {error}", exc_info=True)

    # Check for specific error types
    if isinstance(error, sqlite3.IntegrityError):
        return jsonify(create_error_response(
            code='DUPLICATE_RESOURCE',
            message='Resource already exists or constraint violation',
            details=str(error),
            status_code=409
        )[0]), 409

    return jsonify(create_error_response(
        code='DATABASE_ERROR',
        message='Database operation failed',
        details=str(error),
        status_code=500
    )[0]), 500


def handle_value_error(error):
    """
    Handle ValueError (often indicates validation or not found)

    Args:
        error: ValueError instance

    Returns:
        JSON error response
    """
    error_msg = str(error)
    logger.warning(f"Value error: {error_msg}")

    # Check if it's a "not found" error
    if 'not found' in error_msg.lower():
        return jsonify(create_error_response(
            code='RESOURCE_NOT_FOUND',
            message=error_msg,
            details={},
            status_code=404
        )[0]), 404

    # Otherwise, treat as validation error
    return jsonify(create_error_response(
        code='VALIDATION_ERROR',
        message=error_msg,
        details={},
        status_code=400
    )[0]), 400


def handle_generic_exception(error):
    """
    Handle unexpected exceptions

    Args:
        error: Exception instance

    Returns:
        JSON error response
    """
    logger.error(f"Unexpected error: {error}", exc_info=True)

    # In production, don't expose internal error details
    # In development, include stack trace
    debug_mode = logger.level == logging.DEBUG

    return jsonify(create_error_response(
        code='INTERNAL_ERROR',
        message='An unexpected error occurred',
        details=str(error) if debug_mode else None,
        status_code=500
    )[0]), 500


def register_error_handlers(app):
    """
    Register error handlers with Flask app

    Args:
        app: Flask application instance
    """

    # Handle custom APIError
    @app.errorhandler(APIError)
    def api_error_handler(error):
        return handle_api_error(error)

    # Handle Marshmallow validation errors
    @app.errorhandler(ValidationError)
    def validation_error_handler(error):
        return handle_marshmallow_validation_error(error)

    # Handle database errors
    @app.errorhandler(sqlite3.Error)
    def database_error_handler(error):
        return handle_database_error(error)

    # Handle ValueError
    @app.errorhandler(ValueError)
    def value_error_handler(error):
        return handle_value_error(error)

    # Handle 400 Bad Request
    @app.errorhandler(400)
    def bad_request_handler(error):
        return jsonify(create_error_response(
            code='BAD_REQUEST',
            message='Invalid request',
            details=str(error),
            status_code=400
        )[0]), 400

    # Handle 404 Not Found
    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify(create_error_response(
            code='NOT_FOUND',
            message='Resource not found',
            details={
                'path': request.path,
                'method': request.method
            },
            status_code=404
        )[0]), 404

    # Handle 405 Method Not Allowed
    @app.errorhandler(405)
    def method_not_allowed_handler(error):
        return jsonify(create_error_response(
            code='METHOD_NOT_ALLOWED',
            message='HTTP method not allowed',
            details={
                'path': request.path,
                'method': request.method,
                'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else None
            },
            status_code=405
        )[0]), 405

    # Handle 409 Conflict
    @app.errorhandler(409)
    def conflict_handler(error):
        return jsonify(create_error_response(
            code='CONFLICT',
            message='Resource conflict',
            details=str(error),
            status_code=409
        )[0]), 409

    # Handle 500 Internal Server Error
    @app.errorhandler(500)
    def internal_error_handler(error):
        return handle_generic_exception(error)

    # Handle all other exceptions
    @app.errorhandler(Exception)
    def generic_exception_handler(error):
        return handle_generic_exception(error)

    logger.info("Error handlers registered")


def with_error_handling(func):
    """
    Decorator to add error handling to route functions

    Usage:
        @api_v1_bp.route('/example')
        @with_error_handling
        def example_route():
            # Your code here
            pass

    Args:
        func: Route function to wrap

    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            return handle_api_error(e)
        except ValidationError as e:
            return handle_marshmallow_validation_error(e)
        except sqlite3.Error as e:
            return handle_database_error(e)
        except ValueError as e:
            return handle_value_error(e)
        except Exception as e:
            return handle_generic_exception(e)

    return wrapper


def log_error_context(error, context=None):
    """
    Log error with additional context for debugging

    Args:
        error: Exception instance
        context: Additional context dictionary
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': datetime.now().isoformat(),
        'request_path': request.path if request else None,
        'request_method': request.method if request else None,
        'request_args': dict(request.args) if request else None,
    }

    if context:
        error_info['context'] = context

    logger.error(f"Error details: {error_info}", exc_info=True)


logger.info("Error handling middleware loaded")
