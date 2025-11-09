"""
API Version 1 Blueprint
RESTful API for Pi Zero 2W Medicine Tracker

This module sets up the v1 API blueprint and registers all v1 routes.
"""

import logging
from flask import Blueprint, jsonify
from datetime import datetime

logger = logging.getLogger(__name__)

# Create v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__)


# Import route modules (will be created in Phase 1.3)
# These imports will be uncommented as routes are implemented
try:
    from .routes import medicines, tracking, config as config_routes
    logger.info("Successfully imported v1 route modules")
except ImportError as e:
    logger.warning(f"Some v1 route modules not yet implemented: {e}")


# Blueprint-level error handler
@api_v1_bp.errorhandler(Exception)
def handle_exception(error):
    """
    Handle all uncaught exceptions in v1 API

    Args:
        error: Exception instance

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception in API v1: {error}", exc_info=True)

    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred',
            'details': str(error) if logger.level == logging.DEBUG else None
        },
        'meta': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
    }), 500


# Root endpoint for v1 API
@api_v1_bp.route('/')
def api_root():
    """
    API v1 root endpoint - provides API information

    Returns:
        JSON response with API metadata and available endpoints
    """
    return jsonify({
        'success': True,
        'data': {
            'version': '1.0',
            'name': 'Pi Zero 2W Medicine Tracker API',
            'description': 'RESTful API for medicine tracking and configuration',
            'endpoints': {
                'medicines': '/api/v1/medicines',
                'tracking': '/api/v1/tracking',
                'config': '/api/v1/config',
                'health': '/api/v1/health'
            },
            'documentation': '/api/v1/docs'
        },
        'meta': {
            'timestamp': datetime.now().isoformat()
        }
    }), 200


# API documentation endpoint
@api_v1_bp.route('/docs')
def api_docs():
    """
    API documentation endpoint

    Returns:
        JSON response with API documentation links
    """
    return jsonify({
        'success': True,
        'data': {
            'version': '1.0',
            'documentation': {
                'design': 'See docs/API_DESIGN.md',
                'endpoints': 'See docs/API_ENDPOINT_INVENTORY.md',
                'openapi': 'Coming soon - OpenAPI 3.0 specification'
            },
            'resources': {
                'medicines': {
                    'list': 'GET /api/v1/medicines',
                    'create': 'POST /api/v1/medicines',
                    'get': 'GET /api/v1/medicines/{id}',
                    'update': 'PUT /api/v1/medicines/{id}',
                    'patch': 'PATCH /api/v1/medicines/{id}',
                    'delete': 'DELETE /api/v1/medicines/{id}',
                    'pending': 'GET /api/v1/medicines/pending',
                    'low_stock': 'GET /api/v1/medicines/low-stock',
                    'tracking': 'GET /api/v1/medicines/{id}/tracking',
                    'mark_taken': 'POST /api/v1/medicines/{id}/tracking'
                },
                'tracking': {
                    'list': 'GET /api/v1/tracking',
                    'batch_mark': 'POST /api/v1/tracking',
                    'today_stats': 'GET /api/v1/tracking/today'
                },
                'config': {
                    'get_all': 'GET /api/v1/config',
                    'update_all': 'PUT /api/v1/config',
                    'get_section': 'GET /api/v1/config/{section}',
                    'update_section': 'PATCH /api/v1/config/{section}'
                }
            }
        },
        'meta': {
            'timestamp': datetime.now().isoformat()
        }
    }), 200


logger.info("API v1 blueprint initialized")
