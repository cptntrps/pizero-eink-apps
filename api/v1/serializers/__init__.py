"""
API v1 Serializers Package

This package contains response serializers for API v1.
Serializers format database objects into API responses.
"""

from datetime import datetime


def create_success_response(data=None, message=None, meta=None):
    """
    Create standardized success response

    Args:
        data: Response data (dict, list, or None)
        message: Optional success message
        meta: Optional metadata dict (will be merged with default meta)

    Returns:
        Standardized success response dictionary
    """
    response = {'success': True}

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    # Add metadata
    default_meta = {'timestamp': datetime.now().isoformat()}
    if meta:
        default_meta.update(meta)
    response['meta'] = default_meta

    return response


def create_error_response(code, message, details=None, http_status=400):
    """
    Create standardized error response

    Args:
        code: Error code (string)
        message: Error message
        details: Optional error details (dict or string)
        http_status: HTTP status code

    Returns:
        Tuple of (error response dict, http status code)
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

    return response, http_status


def create_paginated_response(items, total, page, per_page):
    """
    Create paginated response with metadata

    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        per_page: Items per page

    Returns:
        Standardized paginated response dictionary
    """
    total_pages = (total + per_page - 1) // per_page  # Ceiling division

    return create_success_response(
        data=items,
        meta={
            'total': total,
            'count': len(items),
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'timestamp': datetime.now().isoformat()
        }
    )


def serialize_medicine(medicine_dict):
    """
    Serialize medicine database object for API response

    Args:
        medicine_dict: Medicine dictionary from database

    Returns:
        Serialized medicine dictionary
    """
    # Add any additional fields or transformations needed
    # For now, return as-is (database layer already returns clean dicts)
    return medicine_dict


def serialize_tracking_record(tracking_dict):
    """
    Serialize tracking record for API response

    Args:
        tracking_dict: Tracking dictionary from database

    Returns:
        Serialized tracking dictionary
    """
    return tracking_dict
