#!/usr/bin/env python3
"""
Web Configuration Server
A lightweight Flask app that provides a web interface for configuring the Pi Zero 2W system.

This server acts as a proxy/gateway to the main REST API (running on port 5000).
- Medicine endpoints are proxied to the main API at http://localhost:5000/api/v1/
- Configuration endpoints handle: disney, flights, forbidden, system, display, menu
- MBTA, Weather, and Pomodoro apps have been removed

Architecture:
    WebUI (port 5000) --> Proxy --> Main API (port 5000)
"""

import json
import logging
import requests
import sys
import os
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set database path environment variable
os.environ['PIZERO_MEDICINE_DB'] = '/home/pizero2w/pizero_apps/db/medicine.db'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Flask app with custom template and static folders
app = Flask(__name__,
            template_folder='web/templates',
            static_folder='web/static')

# Enable CORS for API integration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
CONFIG_FILE = "/home/pizero2w/pizero_apps/config.json"
MAIN_API_URL = "http://localhost:5000/api/v1"

# Valid configuration sections (excluding deleted apps: mbta, weather, pomodoro)
VALID_CONFIG_SECTIONS = ['disney', 'flights', 'forbidden', 'system', 'display', 'menu', 'medicine']

# ============================================
# REGISTER API BLUEPRINT (Direct Integration)
# ============================================
try:
    from api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')
    logger.info("✓ Registered API v1 blueprint directly on port 5000")
    API_INTEGRATED = True
except ImportError as e:
    logger.warning(f"✗ Could not import API blueprint: {e}")
    logger.warning("Medicine endpoints will not be available")
    API_INTEGRATED = False

# ============================================
# FRONTEND ROUTES
# ============================================

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')


# ============================================
# CONFIGURATION API ENDPOINTS
# ============================================

@app.route('/api/config', methods=['GET'])
def get_config():
    """
    Get all configuration sections (excluding deleted apps)

    Returns:
        JSON object with configuration for: disney, flights, forbidden,
        system, display, menu, medicine
    """
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        # Filter out deleted app sections (mbta, weather, pomodoro)
        filtered_config = {
            k: v for k, v in config.items()
            if k in VALID_CONFIG_SECTIONS
        }

        return jsonify(filtered_config)
    except FileNotFoundError:
        logger.error(f"Config file not found: {CONFIG_FILE}")
        return jsonify({"error": "Configuration file not found"}), 500
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return jsonify({"error": "Invalid configuration file"}), 500
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/<section>', methods=['GET'])
def get_config_section(section):
    """
    Get a specific configuration section

    Args:
        section: Configuration section name (disney, flights, forbidden, system, display, menu, medicine)

    Returns:
        JSON object with section configuration
    """
    # Validate section
    if section not in VALID_CONFIG_SECTIONS:
        return jsonify({
            "error": f"Invalid configuration section: {section}",
            "valid_sections": VALID_CONFIG_SECTIONS
        }), 400

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if section not in config:
            return jsonify({"error": f"Section not found: {section}"}), 404

        return jsonify(config[section])
    except Exception as e:
        logger.error(f"Error reading config section {section}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/<section>', methods=['POST'])
def update_config(section):
    """
    Update a specific configuration section

    Args:
        section: Configuration section name (disney, flights, forbidden, system, display, menu, medicine)

    Request Body:
        JSON object with section configuration

    Returns:
        JSON response with success/error message
    """
    # Validate section
    if section not in VALID_CONFIG_SECTIONS:
        return jsonify({
            "success": False,
            "message": f"Invalid configuration section: {section}",
            "valid_sections": VALID_CONFIG_SECTIONS
        }), 400

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        config[section] = data

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        return jsonify({
            "success": True,
            "message": f"{section.title()} settings saved successfully!"
        })
    except Exception as e:
        logger.error(f"Error updating config section {section}: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


# ============================================
# API PROXY ENDPOINTS
# ============================================

# @app.route('/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
# def proxy_api(path):
#     """
#     Proxy all /api/v1/* requests to the main REST API
# 
#     This allows the WebUI to communicate with the main API running on port 5000.
#     All medicine endpoints, tracking, and other API calls are forwarded here.
# 
#     Args:
#         path: API path after /api/v1/
# 
#     Returns:
#         Response from the main API
#     """
#     try:
#         # Build the target URL
#         target_url = f"{MAIN_API_URL}/{path}"
# 
#         # Get request data
#         headers = {key: value for key, value in request.headers if key.lower() != 'host'}
#         headers['Content-Type'] = 'application/json'
# 
#         # Forward the request to the main API
#         if request.method == 'GET':
#             resp = requests.get(
#                 target_url,
#                 params=request.args,
#                 headers=headers,
#                 timeout=30
#             )
#         elif request.method == 'POST':
#             resp = requests.post(
#                 target_url,
#                 json=request.get_json(),
#                 params=request.args,
#                 headers=headers,
#                 timeout=30
#             )
#         elif request.method == 'PUT':
#             resp = requests.put(
#                 target_url,
#                 json=request.get_json(),
#                 params=request.args,
#                 headers=headers,
#                 timeout=30
#             )
#         elif request.method == 'PATCH':
#             resp = requests.patch(
#                 target_url,
#                 json=request.get_json(),
#                 params=request.args,
#                 headers=headers,
#                 timeout=30
#             )
#         elif request.method == 'DELETE':
#             resp = requests.delete(
#                 target_url,
#                 params=request.args,
#                 headers=headers,
#                 timeout=30
#             )
#         else:
#             return jsonify({"error": "Method not allowed"}), 405
# 
#         # Return the response from the main API
#         return Response(
#             resp.content,
#             status=resp.status_code,
#             headers=dict(resp.headers)
#         )
# 
#     except requests.exceptions.ConnectionError:
#         logger.error(f"Failed to connect to main API at {MAIN_API_URL}")
#         return jsonify({
#             "error": "Main API not available",
#             "message": "The main REST API is not running. Please start it on port 5000.",
#             "api_url": MAIN_API_URL
#         }), 503
#     except requests.exceptions.Timeout:
#         logger.error(f"Request to main API timed out: {target_url}")
#         return jsonify({
#             "error": "Request timeout",
#             "message": "The main API took too long to respond."
#         }), 504
#     except Exception as e:
#         logger.error(f"Error proxying request to {target_url}: {e}")
#         return jsonify({
#             "error": "Proxy error",
#             "message": str(e)
#         }), 500


# ============================================
# HEALTH CHECK
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint

    Returns:
        JSON response with service status
    """
    # Check if main API is accessible
    api_healthy = False
    try:
        resp = requests.get(f"{MAIN_API_URL}/health", timeout=5)
        api_healthy = resp.status_code == 200
    except:
        pass

    return jsonify({
        "status": "healthy",
        "service": "web-config",
        "port": 5000,
        "main_api": {
            "url": MAIN_API_URL,
            "healthy": api_healthy
        }
    })


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    logger.info("Starting Web Configuration Server on port 5000")
    logger.info(f"Main API URL: {MAIN_API_URL}")
    logger.info(f"Valid config sections: {', '.join(VALID_CONFIG_SECTIONS)}")
    logger.info("REMOVED apps: MBTA, Weather, Pomodoro")

    app.run(host='0.0.0.0', port=5000, debug=False)
