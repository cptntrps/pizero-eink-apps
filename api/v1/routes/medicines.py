"""
Medicine Routes - API v1
Handles all medicine-related HTTP endpoints

This is a SAMPLE/STUB implementation to demonstrate the architecture.
Full implementation will be done in Phase 1.3.
"""

import logging
from flask import request, jsonify
from marshmallow import ValidationError

from api.v1 import api_v1_bp
from api.v1.serializers import (
    create_success_response,
    create_error_response,
    create_paginated_response
)
from db.medicine_db import MedicineDatabase
from shared.validation import validate_medicine, format_validation_error

logger = logging.getLogger(__name__)


# ============================================================================
# SAMPLE IMPLEMENTATIONS - Demonstrate architecture pattern
# These will be expanded in Phase 1.3
# ============================================================================


@api_v1_bp.route('/medicines', methods=['GET'])
def list_medicines():
    """
    Get list of medicines with optional filtering and pagination

    Query Parameters:
        - active (bool): Filter by active status
        - time_window (str): Filter by time window
        - low_stock (bool): Filter by low stock status
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)
        - sort (str): Sort field
        - order (str): Sort order (asc/desc)

    Returns:
        200: Paginated list of medicines
        500: Database error
    """
    try:
        # Parse query parameters with bounds validation
        active = request.args.get('active', 'true').lower() == 'true'
        page = max(1, int(request.args.get('page', 1)))  # Page >= 1
        per_page = int(request.args.get('per_page', 20))
        per_page = max(1, min(per_page, 100))  # 1 <= per_page <= 100

        # Get medicines from database
        db = MedicineDatabase()
        medicines = db.get_all_medicines(include_inactive=not active)

        # TODO: Implement filtering, sorting, pagination
        # For now, return all medicines

        return jsonify(create_paginated_response(
            items=medicines,
            total=len(medicines),
            page=page,
            per_page=per_page
        )), 200

    except Exception as e:
        logger.error(f"Failed to list medicines: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve medicines',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines', methods=['POST'])
def create_medicine():
    """
    Create a new medicine

    Request Body:
        JSON object with medicine fields (see MedicineSchema)

    Returns:
        201: Medicine created successfully (with Location header)
        400: Validation error
        409: Duplicate medicine ID
        500: Database error
    """
    try:
        # Get request data
        data = request.get_json()

        # Generate ID if not provided (server-side generation)
        if 'id' not in data:
            from datetime import datetime
            data['id'] = f"med_{int(datetime.now().timestamp() * 1000)}"

        # Validate input
        try:
            validated_data = validate_medicine(data)
        except ValidationError as e:
            return jsonify(format_validation_error(e)), 400

        # Save to database
        db = MedicineDatabase()
        db.add_medicine(validated_data)

        # Return created medicine
        medicine = db.get_medicine_by_id(validated_data['id'])

        response = jsonify(create_success_response(
            data=medicine,
            message='Medicine created successfully'
        ))
        response.status_code = 201
        response.headers['Location'] = f"/api/v1/medicines/{medicine['id']}"

        return response

    except ValidationError as e:
        return jsonify(format_validation_error(e)), 400
    except Exception as e:
        logger.error(f"Failed to create medicine: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to create medicine',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/<medicine_id>', methods=['GET'])
def get_medicine(medicine_id):
    """
    Get a specific medicine by ID

    Path Parameters:
        medicine_id: Medicine ID

    Returns:
        200: Medicine object
        404: Medicine not found
        500: Database error
    """
    try:
        db = MedicineDatabase()
        medicine = db.get_medicine_by_id(medicine_id)

        if not medicine:
            return jsonify(create_error_response(
                code='RESOURCE_NOT_FOUND',
                message='Medicine not found',
                details={'medicine_id': medicine_id}
            )), 404

        return jsonify(create_success_response(data=medicine)), 200

    except Exception as e:
        logger.error(f"Failed to get medicine: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve medicine',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/<medicine_id>', methods=['PUT'])
def update_medicine(medicine_id):
    """
    Replace entire medicine (full update)

    Path Parameters:
        medicine_id: Medicine ID

    Request Body:
        Complete medicine object

    Returns:
        200: Medicine updated successfully
        400: Validation error
        404: Medicine not found
        500: Database error
    """
    try:
        # Get request data
        data = request.get_json()
        data['id'] = medicine_id  # Ensure ID matches path

        # Validate input
        try:
            validated_data = validate_medicine(data)
        except ValidationError as e:
            return jsonify(format_validation_error(e)), 400

        # Update in database
        db = MedicineDatabase()
        db.update_medicine(medicine_id, validated_data)

        # Return updated medicine
        medicine = db.get_medicine_by_id(medicine_id)

        return jsonify(create_success_response(
            data=medicine,
            message='Medicine updated successfully'
        )), 200

    except ValueError as e:
        return jsonify(create_error_response(
            code='RESOURCE_NOT_FOUND',
            message=str(e),
            details={'medicine_id': medicine_id}
        )), 404
    except ValidationError as e:
        return jsonify(format_validation_error(e)), 400
    except Exception as e:
        logger.error(f"Failed to update medicine: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to update medicine',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/<medicine_id>', methods=['PATCH'])
def patch_medicine(medicine_id):
    """
    Partial update of medicine

    Path Parameters:
        medicine_id: Medicine ID

    Request Body:
        Partial medicine object (only fields to update)

    Returns:
        200: Medicine updated successfully
        400: Validation error
        404: Medicine not found
        500: Database error
    """
    try:
        # Get existing medicine
        db = MedicineDatabase()
        medicine = db.get_medicine_by_id(medicine_id)

        if not medicine:
            return jsonify(create_error_response(
                code='RESOURCE_NOT_FOUND',
                message='Medicine not found',
                details={'medicine_id': medicine_id}
            )), 404

        # Merge with updates
        data = request.get_json()
        medicine.update(data)

        # Validate merged data
        try:
            validated_data = validate_medicine(medicine)
        except ValidationError as e:
            return jsonify(format_validation_error(e)), 400

        # Update in database
        db.update_medicine(medicine_id, validated_data)

        # Return updated medicine
        updated_medicine = db.get_medicine_by_id(medicine_id)

        return jsonify(create_success_response(
            data=updated_medicine,
            message='Medicine updated successfully'
        )), 200

    except ValidationError as e:
        return jsonify(format_validation_error(e)), 400
    except Exception as e:
        logger.error(f"Failed to patch medicine: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to update medicine',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/<medicine_id>', methods=['DELETE'])
def delete_medicine(medicine_id):
    """
    Delete a medicine

    Path Parameters:
        medicine_id: Medicine ID

    Returns:
        204: Medicine deleted successfully (no content)
        404: Medicine not found
        500: Database error
    """
    try:
        db = MedicineDatabase()
        db.delete_medicine(medicine_id)

        # Return 204 No Content on successful deletion
        return '', 204

    except ValueError as e:
        return jsonify(create_error_response(
            code='RESOURCE_NOT_FOUND',
            message=str(e),
            details={'medicine_id': medicine_id}
        )), 404
    except Exception as e:
        logger.error(f"Failed to delete medicine: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to delete medicine',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/pending', methods=['GET'])
def get_pending_medicines():
    """
    Get medicines that are due now (within time window)

    Query Parameters:
        - date (str): Check date YYYY-MM-DD (default: today)
        - time (str): Check time HH:MM (default: now)
        - reminder_window (int): Minutes before/after window (default: 30)

    Returns:
        200: List of pending medicines
        500: Database error
    """
    try:
        from datetime import datetime

        # Parse query parameters
        date_str = request.args.get('date')
        time_str = request.args.get('time')
        reminder_window = int(request.args.get('reminder_window', 30))
        # Bounds validation for reminder_window
        reminder_window = max(1, min(reminder_window, 1440))  # 1 minute to 24 hours

        # Parse date/time or use current
        if date_str and time_str:
            try:
                check_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError as e:
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid date/time format. Use YYYY-MM-DD HH:MM',
                    details={'error': str(e)}
                )), 400
        else:
            check_datetime = datetime.now()

        check_date = check_datetime.date()

        # Get pending medicines from database
        db = MedicineDatabase()
        pending = db.get_pending_medicines(check_date=check_date, check_time=check_datetime)

        return jsonify(create_success_response(
            data=pending,
            meta={
                'count': len(pending),
                'checked_at': check_datetime.isoformat(),
                'reminder_window': reminder_window,
                'timestamp': datetime.now().isoformat()
            }
        )), 200

    except Exception as e:
        logger.error(f"Failed to get pending medicines: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve pending medicines',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/low-stock', methods=['GET'])
def get_low_stock_medicines():
    """
    Get medicines with low stock

    Returns:
        200: List of low stock medicines
        500: Database error
    """
    try:
        from datetime import datetime
        db = MedicineDatabase()
        low_stock = db.get_low_stock_medicines()

        return jsonify(create_success_response(
            data=low_stock,
            meta={
                'count': len(low_stock),
                'timestamp': datetime.now().isoformat()
            }
        )), 200

    except Exception as e:
        logger.error(f"Failed to get low stock medicines: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve low stock medicines',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/<medicine_id>/take', methods=['POST'])
def mark_medicine_taken(medicine_id):
    """
    Mark a specific medicine as taken (single medicine convenience endpoint)

    Path Parameters:
        medicine_id: Medicine ID

    Request Body (optional):
        {
            "timestamp": "2025-11-08T08:30:00"  # Optional, defaults to now
        }

    Returns:
        201: Medicine marked as taken
        404: Medicine not found
        500: Database error
    """
    try:
        from datetime import datetime

        # Get optional timestamp from request body
        data = request.get_json() if request.get_json() else {}
        timestamp_str = data.get('timestamp')

        if timestamp_str:
            try:
                # Handle ISO format with 'Z' suffix
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError as e:
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid timestamp format. Use ISO 8601 format',
                    details={'field': 'timestamp', 'error': str(e)}
                )), 400
        else:
            timestamp = datetime.now()

        # Mark medicine as taken
        db = MedicineDatabase()
        result = db.mark_medicine_taken(
            medicine_id=medicine_id,
            timestamp=timestamp,
            taken_date=timestamp.date()
        )

        # Get updated medicine info
        medicine = db.get_medicine_by_id(medicine_id)

        return jsonify(create_success_response(
            data={
                'medicine_id': medicine_id,
                'medicine_name': medicine['name'] if medicine else 'Unknown',
                'pills_remaining': result['pills_remaining'],
                'low_stock': result['low_stock'],
                'taken_at': timestamp.isoformat()
            },
            message='Medicine marked as taken'
        )), 201

    except ValueError as e:
        return jsonify(create_error_response(
            code='RESOURCE_NOT_FOUND',
            message=str(e),
            details={'medicine_id': medicine_id}
        )), 404
    except Exception as e:
        logger.error(f"Failed to mark medicine taken: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to mark medicine as taken',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/batch-take', methods=['POST'])
def batch_mark_taken():
    """
    Mark multiple medicines as taken (batch operation)

    Request Body:
        {
            "medicine_ids": ["med_123", "med_456"],
            "timestamp": "2025-11-08T08:30:00"  # Optional, defaults to now
        }

    Returns:
        200: Medicines marked as taken
        400: Validation error
        500: Database error
    """
    try:
        from datetime import datetime

        # Get request data
        data = request.get_json()

        if not data or 'medicine_ids' not in data:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Missing required field: medicine_ids',
                details={'field': 'medicine_ids'}
            )), 400

        medicine_ids = data['medicine_ids']

        if not isinstance(medicine_ids, list) or len(medicine_ids) == 0:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='medicine_ids must be a non-empty list',
                details={'field': 'medicine_ids'}
            )), 400

        # Get optional timestamp
        timestamp_str = data.get('timestamp')
        if timestamp_str:
            try:
                # Handle ISO format with 'Z' suffix
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError as e:
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid timestamp format. Use ISO 8601 format',
                    details={'field': 'timestamp', 'error': str(e)}
                )), 400
        else:
            timestamp = datetime.now()

        # Mark all medicines as taken
        db = MedicineDatabase()
        marked = []
        errors = []

        for med_id in medicine_ids:
            try:
                result = db.mark_medicine_taken(
                    medicine_id=med_id,
                    timestamp=timestamp,
                    taken_date=timestamp.date()
                )

                # Get medicine info
                medicine = db.get_medicine_by_id(med_id)

                marked.append({
                    'id': med_id,
                    'name': medicine['name'] if medicine else 'Unknown',
                    'pills_remaining': result['pills_remaining'],
                    'low_stock': result['low_stock']
                })
            except Exception as e:
                logger.error(f"Failed to mark medicine {med_id} as taken: {e}")
                errors.append({
                    'id': med_id,
                    'error': str(e)
                })

        # Return results
        response_data = {
            'marked': marked,
            'timestamp': timestamp.isoformat()
        }

        if errors:
            response_data['errors'] = errors

        return jsonify(create_success_response(
            data=response_data,
            message=f"Marked {len(marked)} medicine(s) as taken",
            meta={
                'count': len(marked),
                'error_count': len(errors),
                'timestamp': datetime.now().isoformat()
            }
        )), 200

    except Exception as e:
        logger.error(f"Batch mark taken failed: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to mark medicines as taken',
            details=str(e)
        )), 500


# ============================================================================
# NOTE: Tracking endpoints (/medicines/{id}/tracking) will be implemented
# in tracking.py to keep concerns separated
# ============================================================================

logger.info("Medicine routes registered")
