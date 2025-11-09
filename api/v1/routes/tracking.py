"""
Tracking Routes - API v1
Handles all tracking-related HTTP endpoints

This module provides endpoints for tracking medicine adherence,
viewing history, and getting statistics.
"""

import logging
from datetime import datetime, date, timedelta
from flask import request, jsonify

from api.v1 import api_v1_bp
from api.v1.serializers import (
    create_success_response,
    create_error_response,
    create_paginated_response
)
from db.medicine_db import MedicineDatabase
from shared.validation import validate_date_format, validate_skip_medicine
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


@api_v1_bp.route('/medicines/<medicine_id>/tracking', methods=['GET'])
def get_medicine_tracking(medicine_id):
    """
    Get tracking history for a specific medicine

    Path Parameters:
        medicine_id: Medicine ID

    Query Parameters:
        - start_date (str): Start date YYYY-MM-DD (optional)
        - end_date (str): End date YYYY-MM-DD (optional)
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)

    Returns:
        200: Paginated tracking history
        404: Medicine not found
        400: Invalid date format
        500: Database error
    """
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)

        # Validate date formats
        start_date = None
        end_date = None

        if start_date_str:
            if not validate_date_format(start_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid start_date format. Use YYYY-MM-DD',
                    details={'field': 'start_date'}
                )), 400
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        if end_date_str:
            if not validate_date_format(end_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid end_date format. Use YYYY-MM-DD',
                    details={'field': 'end_date'}
                )), 400
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get tracking history
        db = MedicineDatabase()

        # Check if medicine exists
        medicine = db.get_medicine_by_id(medicine_id)
        if not medicine:
            return jsonify(create_error_response(
                code='RESOURCE_NOT_FOUND',
                message='Medicine not found',
                details={'medicine_id': medicine_id}
            )), 404

        # Get tracking records
        tracking_records = db.get_tracking_history(
            medicine_id=medicine_id,
            start_date=start_date,
            end_date=end_date
        )

        # Pagination
        total = len(tracking_records)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = tracking_records[start_idx:end_idx]

        return jsonify(create_paginated_response(
            items=paginated_records,
            total=total,
            page=page,
            per_page=per_page
        )), 200

    except Exception as e:
        logger.error(f"Failed to get tracking history: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve tracking history',
            details=str(e)
        )), 500


@api_v1_bp.route('/medicines/<medicine_id>/tracking', methods=['POST'])
def mark_specific_medicine_taken(medicine_id):
    """
    Mark a specific medicine as taken (tracking endpoint)

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


@api_v1_bp.route('/tracking', methods=['GET'])
def get_all_tracking():
    """
    Get tracking history for all medicines with filtering

    Query Parameters:
        - medicine_id (str): Filter by medicine ID (optional)
        - start_date (str): Start date YYYY-MM-DD (optional)
        - end_date (str): End date YYYY-MM-DD (optional)
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)

    Returns:
        200: Paginated tracking history
        400: Invalid parameters
        500: Database error
    """
    try:
        # Parse query parameters with bounds validation
        medicine_id = request.args.get('medicine_id')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        page = max(1, int(request.args.get('page', 1)))  # Page >= 1
        per_page = int(request.args.get('per_page', 20))
        per_page = max(1, min(per_page, 100))  # 1 <= per_page <= 100

        # Validate date formats
        start_date = None
        end_date = None

        if start_date_str:
            if not validate_date_format(start_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid start_date format. Use YYYY-MM-DD',
                    details={'field': 'start_date'}
                )), 400
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        if end_date_str:
            if not validate_date_format(end_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid end_date format. Use YYYY-MM-DD',
                    details={'field': 'end_date'}
                )), 400
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get tracking history
        db = MedicineDatabase()
        tracking_records = db.get_tracking_history(
            medicine_id=medicine_id,
            start_date=start_date,
            end_date=end_date
        )

        # Pagination
        total = len(tracking_records)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = tracking_records[start_idx:end_idx]

        return jsonify(create_paginated_response(
            items=paginated_records,
            total=total,
            page=page,
            per_page=per_page
        )), 200

    except Exception as e:
        logger.error(f"Failed to get tracking history: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve tracking history',
            details=str(e)
        )), 500


@api_v1_bp.route('/tracking', methods=['POST'])
def batch_mark_medicines_taken():
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


@api_v1_bp.route('/tracking/today', methods=['GET'])
def get_today_stats():
    """
    Get today's adherence statistics

    Query Parameters:
        - date (str): Check date YYYY-MM-DD (default: today)

    Returns:
        200: Today's statistics
        400: Invalid date format
        500: Database error
    """
    try:
        # Parse query parameters
        date_str = request.args.get('date')

        # Validate date format
        check_date = None
        if date_str:
            if not validate_date_format(date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid date format. Use YYYY-MM-DD',
                    details={'field': 'date'}
                )), 400
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            check_date = date.today()

        # Get statistics
        db = MedicineDatabase()
        medicines_taken, medicines_skipped, total_medicines = db.get_today_stats(check_date=check_date)

        # Get low stock count
        low_stock = db.get_low_stock_medicines()
        low_stock_count = len(low_stock)

        # Calculate adherence rate
        adherence_rate = medicines_taken / total_medicines if total_medicines > 0 else 0.0

        # Get pending medicines (not taken and not skipped)
        pending_medicines = total_medicines - medicines_taken - medicines_skipped

        return jsonify(create_success_response(
            data={
                'date': check_date.strftime('%Y-%m-%d'),
                'total_medicines': total_medicines,
                'medicines_taken': medicines_taken,
                'medicines_skipped': medicines_skipped,
                'medicines_pending': pending_medicines,
                'adherence_rate': round(adherence_rate, 2),
                'low_stock_count': low_stock_count
            }
        )), 200

    except Exception as e:
        logger.error(f"Failed to get today's stats: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve statistics',
            details=str(e)
        )), 500


@api_v1_bp.route('/tracking/stats', methods=['GET'])
def get_adherence_stats():
    """
    Get adherence statistics over a period

    Query Parameters:
        - start_date (str): Start date YYYY-MM-DD (default: 7 days ago)
        - end_date (str): End date YYYY-MM-DD (default: today)
        - medicine_id (str): Filter by medicine ID (optional)

    Returns:
        200: Adherence statistics
        400: Invalid parameters
        500: Database error
    """
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        medicine_id = request.args.get('medicine_id')

        # Default to last 7 days if not specified
        if not end_date_str:
            end_date = date.today()
        else:
            if not validate_date_format(end_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid end_date format. Use YYYY-MM-DD',
                    details={'field': 'end_date'}
                )), 400
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if not start_date_str:
            start_date = end_date - timedelta(days=7)
        else:
            if not validate_date_format(start_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid start_date format. Use YYYY-MM-DD',
                    details={'field': 'start_date'}
                )), 400
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        # Get tracking history
        db = MedicineDatabase()
        tracking_records = db.get_tracking_history(
            medicine_id=medicine_id,
            start_date=start_date,
            end_date=end_date
        )

        # Calculate statistics
        total_records = len(tracking_records)
        taken_records = len([r for r in tracking_records if r.get('taken', False)])
        adherence_rate = taken_records / total_records if total_records > 0 else 0.0

        # Group by date for daily breakdown
        daily_stats = {}
        for record in tracking_records:
            record_date = record.get('date')
            if record_date not in daily_stats:
                daily_stats[record_date] = {
                    'date': record_date,
                    'total': 0,
                    'taken': 0
                }
            daily_stats[record_date]['total'] += 1
            if record.get('taken', False):
                daily_stats[record_date]['taken'] += 1

        # Calculate daily adherence rates
        for day_data in daily_stats.values():
            day_data['adherence_rate'] = round(
                day_data['taken'] / day_data['total'] if day_data['total'] > 0 else 0.0,
                2
            )

        return jsonify(create_success_response(
            data={
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': (end_date - start_date).days + 1
                },
                'overall': {
                    'total_records': total_records,
                    'taken_records': taken_records,
                    'adherence_rate': round(adherence_rate, 2)
                },
                'daily': sorted(daily_stats.values(), key=lambda x: x['date'], reverse=True)
            }
        )), 200

    except Exception as e:
        logger.error(f"Failed to get adherence stats: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve adherence statistics',
            details=str(e)
        )), 500


@api_v1_bp.route('/tracking/skip', methods=['POST'])
def skip_medicine():
    """
    Skip a medicine dose

    Request Body:
        {
            "medicine_id": "med_xxx",
            "time_window": "morning",  # Optional
            "skip_reason": "Forgot" | "Side effects" | "Out of stock" | "Doctor advised" | "Other",
            "skip_date": "2025-11-08",  # Optional, defaults to today
            "notes": "Additional notes"  # Optional
        }

    Returns:
        201: Medicine marked as skipped
        400: Validation error
        404: Medicine not found
        500: Database error
    """
    try:
        # Get request data
        data = request.get_json()

        if not data:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Request body is required',
                details={'field': 'body'}
            )), 400

        # Validate input
        try:
            validated_data = validate_skip_medicine(data)
        except ValidationError as e:
            return jsonify(create_error_response(
                code='VALIDATION_ERROR',
                message='Validation failed',
                details=e.messages
            )), 400

        # Extract validated fields
        medicine_id = validated_data['medicine_id']
        time_window = validated_data.get('time_window')
        skip_date_obj = validated_data.get('skip_date', date.today())
        skip_reason = validated_data.get('skip_reason')

        # Skip the medicine
        db = MedicineDatabase()
        result = db.skip_medicine(
            medicine_id=medicine_id,
            time_window=time_window,
            skip_date=skip_date_obj,
            skip_timestamp=datetime.now(),
            skip_reason=skip_reason
        )

        # Get medicine info
        medicine = db.get_medicine_by_id(medicine_id)

        return jsonify(create_success_response(
            data={
                'medicine_id': medicine_id,
                'medicine_name': medicine['name'] if medicine else 'Unknown',
                'skip_date': result['skip_date'],
                'skip_timestamp': result['skip_timestamp'],
                'skip_reason': skip_reason,
                'time_window': result['time_window']
            },
            message='Medicine marked as skipped'
        )), 201

    except ValueError as e:
        return jsonify(create_error_response(
            code='RESOURCE_NOT_FOUND',
            message=str(e),
            details={'medicine_id': data.get('medicine_id')}
        )), 404
    except Exception as e:
        logger.error(f"Failed to skip medicine: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to skip medicine',
            details=str(e)
        )), 500


@api_v1_bp.route('/tracking/skip-history', methods=['GET'])
def get_skip_history():
    """
    Get skip history

    Query Parameters:
        - medicine_id (str): Filter by medicine ID (optional)
        - start_date (str): Start date YYYY-MM-DD (optional)
        - end_date (str): End date YYYY-MM-DD (optional)
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)

    Returns:
        200: Skip history
        400: Invalid parameters
        500: Database error
    """
    try:
        # Parse query parameters
        medicine_id = request.args.get('medicine_id')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        page = max(1, int(request.args.get('page', 1)))
        per_page = int(request.args.get('per_page', 20))
        per_page = max(1, min(per_page, 100))

        # Validate date formats
        start_date = None
        end_date = None

        if start_date_str:
            if not validate_date_format(start_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid start_date format. Use YYYY-MM-DD',
                    details={'field': 'start_date'}
                )), 400
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        if end_date_str:
            if not validate_date_format(end_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid end_date format. Use YYYY-MM-DD',
                    details={'field': 'end_date'}
                )), 400
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get skip history
        db = MedicineDatabase()
        skip_records = db.get_skip_history(
            medicine_id=medicine_id,
            start_date=start_date,
            end_date=end_date
        )

        # Pagination
        total = len(skip_records)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = skip_records[start_idx:end_idx]

        return jsonify(create_paginated_response(
            items=paginated_records,
            total=total,
            page=page,
            per_page=per_page
        )), 200

    except Exception as e:
        logger.error(f"Failed to get skip history: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve skip history',
            details=str(e)
        )), 500


@api_v1_bp.route('/tracking/adherence-detailed', methods=['GET'])
def get_adherence_detailed():
    """
    Get detailed adherence stats including skips

    Query Parameters:
        - start_date (str): Start date YYYY-MM-DD (optional, defaults to 30 days ago)
        - end_date (str): End date YYYY-MM-DD (optional, defaults to today)

    Response:
        {
            "taken": 45,
            "skipped": 3,
            "missed": 2,
            "total": 50,
            "adherence_rate": 90.0,
            "skip_rate": 6.0
        }

    Returns:
        200: Detailed adherence statistics
        400: Invalid parameters
        500: Database error
    """
    try:
        # Parse query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Validate date formats
        start_date = None
        end_date = None

        if start_date_str:
            if not validate_date_format(start_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid start_date format. Use YYYY-MM-DD',
                    details={'field': 'start_date'}
                )), 400
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

        if end_date_str:
            if not validate_date_format(end_date_str):
                return jsonify(create_error_response(
                    code='VALIDATION_ERROR',
                    message='Invalid end_date format. Use YYYY-MM-DD',
                    details={'field': 'end_date'}
                )), 400
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get detailed adherence stats
        db = MedicineDatabase()
        stats = db.get_adherence_detailed(
            start_date=start_date,
            end_date=end_date
        )

        return jsonify(create_success_response(
            data=stats
        )), 200

    except Exception as e:
        logger.error(f"Failed to get detailed adherence stats: {e}")
        return jsonify(create_error_response(
            code='DATABASE_ERROR',
            message='Failed to retrieve detailed adherence statistics',
            details=str(e)
        )), 500


logger.info("Tracking routes registered")
