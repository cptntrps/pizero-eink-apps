"""
Input Validation Schemas
Marshmallow schemas for validating API inputs and data integrity
"""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from datetime import datetime


class MedicineSchema(Schema):
    """Schema for medicine data validation"""

    id = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^med_\d+$',
            error='Medicine ID must be in format: med_TIMESTAMP'
        )
    )

    name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=50,
            error='Medicine name must be between 1 and 50 characters'
        )
    )

    dosage = fields.Str(
        required=True,
        validate=validate.Length(
            min=1,
            max=20,
            error='Dosage must be between 1 and 20 characters'
        )
    )

    time_window = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['morning', 'afternoon', 'evening', 'night'],
            error='Time window must be one of: morning, afternoon, evening, night'
        )
    )

    window_start = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^\d{2}:\d{2}$',
            error='Window start must be in format HH:MM'
        )
    )

    window_end = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^\d{2}:\d{2}$',
            error='Window end must be in format HH:MM'
        )
    )

    days = fields.List(
        fields.Str(
            validate=validate.OneOf(
                ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                error='Day must be one of: mon, tue, wed, thu, fri, sat, sun'
            )
        ),
        required=True,
        validate=validate.Length(
            min=1,
            max=7,
            error='Must specify at least one day, maximum 7 days'
        )
    )

    with_food = fields.Bool(required=True)

    notes = fields.Str(
        allow_none=True,
        validate=validate.Length(
            max=100,
            error='Notes must be 100 characters or less'
        )
    )

    pills_remaining = fields.Int(
        required=True,
        validate=validate.Range(
            min=0,
            max=1000,
            error='Pills remaining must be between 0 and 1000'
        )
    )

    pills_per_dose = fields.Int(
        required=True,
        validate=validate.Range(
            min=1,
            max=10,
            error='Pills per dose must be between 1 and 10'
        )
    )

    low_stock_threshold = fields.Int(
        required=True,
        validate=validate.Range(
            min=1,
            max=100,
            error='Low stock threshold must be between 1 and 100'
        )
    )

    active = fields.Bool(required=True)

    @validates('window_start')
    def validate_window_start(self, value, **kwargs):
        """Validate window start time format"""
        try:
            hours, minutes = map(int, value.split(':'))
            if hours < 0 or hours > 23:
                raise ValidationError('Hours must be between 00 and 23')
            if minutes < 0 or minutes > 59:
                raise ValidationError('Minutes must be between 00 and 59')
        except ValueError:
            raise ValidationError('Invalid time format')

    @validates('window_end')
    def validate_window_end(self, value, **kwargs):
        """Validate window end time format"""
        try:
            hours, minutes = map(int, value.split(':'))
            if hours < 0 or hours > 23:
                raise ValidationError('Hours must be between 00 and 23')
            if minutes < 0 or minutes > 59:
                raise ValidationError('Minutes must be between 00 and 59')
        except ValueError:
            raise ValidationError('Invalid time format')

    @validates_schema
    def validate_window_times(self, data, **kwargs):
        """Validate that window_end is after window_start"""
        if 'window_start' in data and 'window_end' in data:
            start = data['window_start']
            end = data['window_end']

            start_mins = int(start.split(':')[0]) * 60 + int(start.split(':')[1])
            end_mins = int(end.split(':')[0]) * 60 + int(end.split(':')[1])

            if end_mins <= start_mins:
                raise ValidationError(
                    'Window end time must be after window start time',
                    field_name='window_end'
                )

    @validates_schema
    def validate_stock_levels(self, data, **kwargs):
        """Validate stock thresholds make sense"""
        if 'pills_remaining' in data and 'low_stock_threshold' in data:
            if data['pills_remaining'] < 0:
                raise ValidationError(
                    'Pills remaining cannot be negative',
                    field_name='pills_remaining'
                )


class MarkTakenSchema(Schema):
    """Schema for mark medicine taken request"""

    medicine_id = fields.Str(
        validate=validate.Regexp(
            r'^med_\d+$',
            error='Medicine ID must be in format: med_TIMESTAMP'
        )
    )

    medicine_ids = fields.List(
        fields.Str(
            validate=validate.Regexp(
                r'^med_\d+$',
                error='Medicine ID must be in format: med_TIMESTAMP'
            )
        ),
        validate=validate.Length(
            min=1,
            max=20,
            error='Must specify 1-20 medicine IDs'
        )
    )

    timestamp = fields.DateTime(allow_none=True)

    @validates_schema
    def validate_medicine_id_field(self, data, **kwargs):
        """Ensure either medicine_id or medicine_ids is provided"""
        if 'medicine_id' not in data and 'medicine_ids' not in data:
            raise ValidationError('Must provide either medicine_id or medicine_ids')

        if 'medicine_id' in data and 'medicine_ids' in data:
            raise ValidationError('Cannot provide both medicine_id and medicine_ids')


class SkipMedicineSchema(Schema):
    """Schema for skipping a medicine dose"""

    medicine_id = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^med_.+$',
            error='Medicine ID must be in format: med_*'
        )
    )

    time_window = fields.Str(
        validate=validate.OneOf(
            ['morning', 'afternoon', 'evening', 'night'],
            error='Time window must be one of: morning, afternoon, evening, night'
        )
    )

    skip_date = fields.Date(format='%Y-%m-%d')

    skip_reason = fields.Str(
        validate=validate.OneOf(
            ['Forgot', 'Side effects', 'Out of stock', 'Doctor advised', 'Other'],
            error='Skip reason must be one of: Forgot, Side effects, Out of stock, Doctor advised, Other'
        )
    )

    notes = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True
    )


class ConfigUpdateSchema(Schema):
    """Schema for configuration updates"""

    # Flexible schema - validate specific sections based on type
    pass


def validate_medicine(data: dict) -> dict:
    """Validate medicine data and return cleaned data

    Args:
        data: Raw medicine data dictionary

    Returns:
        Validated and cleaned medicine data

    Raises:
        ValidationError: If validation fails
    """
    schema = MedicineSchema()
    return schema.load(data)


def validate_mark_taken(data: dict) -> dict:
    """Validate mark taken request

    Args:
        data: Raw request data

    Returns:
        Validated request data

    Raises:
        ValidationError: If validation fails
    """
    schema = MarkTakenSchema()
    return schema.load(data)


def validate_skip_medicine(data: dict) -> dict:
    """Validate skip medicine data

    Args:
        data: Raw skip medicine data

    Returns:
        Validated skip medicine data

    Raises:
        ValidationError: If validation fails
    """
    schema = SkipMedicineSchema()
    return schema.load(data)


def validate_time_format(time_str: str) -> bool:
    """Validate time string is in HH:MM format

    Args:
        time_str: Time string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        hours, minutes = map(int, time_str.split(':'))
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except BaseException:
        return False


def validate_date_format(date_str: str) -> bool:
    """Validate date string is in YYYY-MM-DD format

    Args:
        date_str: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except BaseException:
        return False


def sanitize_string(value: str, max_length: int = 100) -> str:
    """Sanitize string input (remove dangerous characters, limit length)

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ''

    # Remove control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char == '\n')

    # Truncate to max length
    sanitized = sanitized[:max_length]

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def validate_positive_integer(value: int, min_val: int = 0, max_val: int = None) -> bool:
    """Validate integer is positive and within range

    Args:
        value: Integer to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive), None for no maximum

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(value, int):
        return False

    if value < min_val:
        return False

    if max_val is not None and value > max_val:
        return False

    return True


# Error response helpers
def format_validation_error(error: ValidationError) -> dict:
    """Format Marshmallow validation error for API response

    Args:
        error: ValidationError from Marshmallow

    Returns:
        Dictionary with formatted error messages
    """
    return {
        'success': False,
        'error': 'Validation failed',
        'details': error.messages
    }


def create_error_response(message: str, details: dict = None) -> dict:
    """Create standardized error response

    Args:
        message: Error message
        details: Optional details dictionary

    Returns:
        Error response dictionary
    """
    response = {
        'success': False,
        'error': message
    }

    if details:
        response['details'] = details

    return response


def create_success_response(data: dict = None, message: str = None) -> dict:
    """Create standardized success response

    Args:
        data: Response data
        message: Success message

    Returns:
        Success response dictionary
    """
    response = {'success': True}

    if message:
        response['message'] = message

    if data:
        response['data'] = data

    return response
