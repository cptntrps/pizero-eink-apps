#!/usr/bin/env python3
"""
Run the Flask API Server
Development server for testing the RESTful API
"""

from api import create_app
import os
import sys
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Create Flask app
    app = create_app('development')

    # Get configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    logger.info(f"Starting Flask API server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"API Version: v1")
    logger.info(f"Base URL: http://{host}:{port}/api/v1")

    # Run server
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
