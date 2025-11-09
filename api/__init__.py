"""
Pi Zero 2W Medicine Tracker API
Flask Application Factory

This module provides the Flask app factory for the RESTful API.
Supports multiple API versions and extension management.
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """
    Flask application factory

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(get_config(config_name))

    # Enable CORS for development
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register health check
    register_health_check(app)

    # Log startup
    logger.info("Flask app created with config: %s", config_name)
    logger.info("API Version: %s", app.config.get('API_VERSION', '1.0.0'))

    return app


def get_config(config_name):
    """
    Get configuration object based on environment

    Args:
        config_name: Configuration name

    Returns:
        Configuration object
    """
    from .config import config_map
    return config_map.get(config_name, config_map['development'])


def register_blueprints(app):
    """
    Register all API version blueprints

    Args:
        app: Flask application instance
    """
    # Import and register v1 API
    from .v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    logger.info("Registered API v1 blueprint at /api/v1")

    # Future: Register v2, v3, etc.
    # from .v2 import api_v2_bp
    # app.register_blueprint(api_v2_bp, url_prefix='/api/v2')


def register_error_handlers(app):
    """
    Register global error handlers

    Args:
        app: Flask application instance
    """

    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': 'Invalid request',
                'details': str(error)
            },
            'meta': {
                'timestamp': datetime.now().isoformat()
            }
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found',
                'details': str(error)
            },
            'meta': {
                'timestamp': datetime.now().isoformat()
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'HTTP method not allowed',
                'details': str(error)
            },
            'meta': {
                'timestamp': datetime.now().isoformat()
            }
        }), 405

    @app.errorhandler(409)
    def conflict(error):
        """Handle 409 Conflict errors"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'CONFLICT',
                'message': 'Resource conflict',
                'details': str(error)
            },
            'meta': {
                'timestamp': datetime.now().isoformat()
            }
        }), 409

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        logger.error("Internal server error: %s", error)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': 'An unexpected error occurred'
            },
            'meta': {
                'timestamp': datetime.now().isoformat()
            }
        }), 500

    logger.info("Registered global error handlers")


def register_health_check(app):
    """
    Register health check endpoint

    Args:
        app: Flask application instance
    """

    @app.route('/api/health')
    @app.route('/api/v1/health')
    def health_check():
        """API health check endpoint"""
        import time

        # Check database connectivity
        db_status = 'unknown'
        try:
            from db.medicine_db import MedicineDatabase
            db = MedicineDatabase()
            # Simple query to test connection
            db.get_all_medicines()
            db_status = 'connected'
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Database health check failed: %s", e)
            db_status = 'disconnected'

        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy' if db_status == 'connected' else 'degraded',
                'version': app.config.get('API_VERSION', '1.0.0'),
                'database': db_status,
                'timestamp': datetime.now().isoformat()
            },
            'meta': {
                'timestamp': datetime.now().isoformat()
            }
        }), 200

    logger.info("Registered health check endpoint")


# Application factory function for production use
def create_production_app():
    """Create production Flask app"""
    return create_app('production')


# Application factory function for development use
def create_development_app():
    """Create development Flask app"""
    return create_app('development')


# Application factory function for testing use
def create_testing_app():
    """Create testing Flask app"""
    return create_app('testing')
