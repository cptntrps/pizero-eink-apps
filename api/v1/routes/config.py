"""
Configuration Routes - API v1
Handles all configuration-related HTTP endpoints

This module provides endpoints for reading and updating application configuration.
Configuration is stored in config.json and includes settings for all app modules.
"""

import os
import json
import logging
from flask import request, jsonify
from threading import Lock

from api.v1 import api_v1_bp
from api.v1.serializers import create_success_response, create_error_response

logger = logging.getLogger(__name__)

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.json')

# Thread-safe lock for config file operations
config_lock = Lock()

# Valid configuration sections (REMOVED: weather, mbta, pomodoro - apps deleted in Phase 4)
VALID_SECTIONS = [
    'disney', 'flights', 'forbidden', 'medicine', 'menu', 'system', 'display'
]


def load_config():
    """
    Load configuration from config.json

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    with config_lock:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)


def save_config(config_data):
    """
    Save configuration to config.json

    Args:
        config_data: Configuration dictionary to save

    Raises:
        IOError: If unable to write to config file
    """
    with config_lock:
        # Write to temporary file first
        temp_file = CONFIG_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(config_data, f, indent=2)

        # Atomic rename
        os.replace(temp_file, CONFIG_FILE)


@api_v1_bp.route('/config', methods=['GET'])
def get_all_config():
    """
    Get entire configuration

    Returns:
        200: All configuration sections
        500: Error reading configuration
    """
    try:
        config = load_config()

        return jsonify(create_success_response(
            data=config
        )), 200

    except FileNotFoundError:
        logger.error("Config file not found")
        return jsonify(create_error_response(
            code='FILE_NOT_FOUND',
            message='Configuration file not found',
            details={'file': CONFIG_FILE}
        )), 500
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return jsonify(create_error_response(
            code='INVALID_CONFIG',
            message='Configuration file is invalid',
            details=str(e)
        )), 500
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return jsonify(create_error_response(
            code='INTERNAL_ERROR',
            message='Failed to load configuration',
            details=str(e)
        )), 500


@api_v1_bp.route('/config/<section>', methods=['GET'])
def get_config_section(section):
    """
    Get specific configuration section

    Path Parameters:
        section: Configuration section name

    Returns:
        200: Configuration section data
        404: Section not found
        500: Error reading configuration
    """
    try:
        config = load_config()

        if section not in config:
            return jsonify(create_error_response(
                code='SECTION_NOT_FOUND',
                message=f'Configuration section not found: {section}',
                details={
                    'section': section,
                    'available_sections': list(config.keys())
                }
            )), 404

        return jsonify(create_success_response(
            data=config[section]
        )), 200

    except FileNotFoundError:
        logger.error("Config file not found")
        return jsonify(create_error_response(
            code='FILE_NOT_FOUND',
            message='Configuration file not found',
            details={'file': CONFIG_FILE}
        )), 500
    except Exception as e:
        logger.error(f"Failed to load config section: {e}")
        return jsonify(create_error_response(
            code='INTERNAL_ERROR',
            message='Failed to load configuration section',
            details=str(e)
        )), 500


@api_v1_bp.route('/config', methods=['PUT'])
def update_all_config():
    """
    Replace entire configuration (full update)

    Request Body:
        Complete configuration object

    Returns:
        200: Configuration updated successfully
        400: Invalid configuration data
        500: Error saving configuration
    """
    try:
        new_config = request.get_json()

        if not new_config:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Request body is empty or invalid JSON',
                details={}
            )), 400

        # Validate that it's a dictionary
        if not isinstance(new_config, dict):
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Configuration must be a JSON object',
                details={}
            )), 400

        # Save configuration
        save_config(new_config)

        return jsonify(create_success_response(
            data=new_config,
            message='Configuration updated successfully'
        )), 200

    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return jsonify(create_error_response(
            code='INTERNAL_ERROR',
            message='Failed to update configuration',
            details=str(e)
        )), 500


@api_v1_bp.route('/config/<section>', methods=['PUT'])
def replace_config_section(section):
    """
    Replace entire configuration section (full update)

    Path Parameters:
        section: Configuration section name

    Request Body:
        Complete section object

    Returns:
        200: Configuration section updated
        400: Invalid data
        404: Section not found
        500: Error saving configuration
    """
    try:
        config = load_config()

        if section not in config:
            return jsonify(create_error_response(
                code='SECTION_NOT_FOUND',
                message=f'Configuration section not found: {section}',
                details={
                    'section': section,
                    'available_sections': list(config.keys())
                }
            )), 404

        new_section_data = request.get_json()

        if not new_section_data:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Request body is empty or invalid JSON',
                details={}
            )), 400

        # Update section
        config[section] = new_section_data

        # Save configuration
        save_config(config)

        return jsonify(create_success_response(
            data=config[section],
            message=f'{section.capitalize()} configuration updated successfully'
        )), 200

    except Exception as e:
        logger.error(f"Failed to update config section: {e}")
        return jsonify(create_error_response(
            code='INTERNAL_ERROR',
            message='Failed to update configuration section',
            details=str(e)
        )), 500


@api_v1_bp.route('/config/<section>', methods=['PATCH'])
def patch_config_section(section):
    """
    Partial update of configuration section

    Path Parameters:
        section: Configuration section name

    Request Body:
        Partial section object (only fields to update)

    Returns:
        200: Configuration section updated
        400: Invalid data
        404: Section not found
        500: Error saving configuration
    """
    try:
        config = load_config()

        if section not in config:
            return jsonify(create_error_response(
                code='SECTION_NOT_FOUND',
                message=f'Configuration section not found: {section}',
                details={
                    'section': section,
                    'available_sections': list(config.keys())
                }
            )), 404

        updates = request.get_json()

        if not updates:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Request body is empty or invalid JSON',
                details={}
            )), 400

        if not isinstance(updates, dict):
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Update data must be a JSON object',
                details={}
            )), 400

        # Merge updates with existing section
        if isinstance(config[section], dict):
            config[section].update(updates)
        else:
            # If section is not a dict, replace it entirely
            config[section] = updates

        # Save configuration
        save_config(config)

        return jsonify(create_success_response(
            data=config[section],
            message=f'{section.capitalize()} configuration updated successfully'
        )), 200

    except Exception as e:
        logger.error(f"Failed to patch config section: {e}")
        return jsonify(create_error_response(
            code='INTERNAL_ERROR',
            message='Failed to update configuration section',
            details=str(e)
        )), 500


# Section-specific convenience endpoints (optional, for better organization)
# REMOVED: weather, mbta, pomodoro - apps deleted in Phase 4

@api_v1_bp.route('/config/disney', methods=['GET', 'PUT', 'PATCH'])
def disney_config():
    """Disney configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('disney')
    elif request.method == 'PUT':
        return replace_config_section('disney')
    elif request.method == 'PATCH':
        return patch_config_section('disney')


@api_v1_bp.route('/config/flights', methods=['GET', 'PUT', 'PATCH'])
def flights_config():
    """Flights configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('flights')
    elif request.method == 'PUT':
        return replace_config_section('flights')
    elif request.method == 'PATCH':
        return patch_config_section('flights')


@api_v1_bp.route('/config/forbidden', methods=['GET', 'PUT', 'PATCH'])
def forbidden_config():
    """Forbidden configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('forbidden')
    elif request.method == 'PUT':
        return replace_config_section('forbidden')
    elif request.method == 'PATCH':
        return patch_config_section('forbidden')


@api_v1_bp.route('/config/medicine', methods=['GET', 'PUT', 'PATCH'])
def medicine_config():
    """Medicine configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('medicine')
    elif request.method == 'PUT':
        return replace_config_section('medicine')
    elif request.method == 'PATCH':
        return patch_config_section('medicine')


@api_v1_bp.route('/config/menu', methods=['GET', 'PUT', 'PATCH'])
def menu_config():
    """Menu configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('menu')
    elif request.method == 'PUT':
        return replace_config_section('menu')
    elif request.method == 'PATCH':
        return patch_config_section('menu')


@api_v1_bp.route('/config/system', methods=['GET', 'PUT', 'PATCH'])
def system_config():
    """System configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('system')
    elif request.method == 'PUT':
        return replace_config_section('system')
    elif request.method == 'PATCH':
        return patch_config_section('system')


@api_v1_bp.route('/config/display', methods=['GET', 'PUT', 'PATCH'])
def display_config():
    """Display configuration endpoint (convenience wrapper)"""
    if request.method == 'GET':
        return get_config_section('display')
    elif request.method == 'PUT':
        return replace_config_section('display')
    elif request.method == 'PATCH':
        return patch_config_section('display')


logger.info("Configuration routes registered")
