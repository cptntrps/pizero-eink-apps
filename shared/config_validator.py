"""
Configuration Validation Schemas
Pydantic and custom validators for application configuration
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import logging
import json
from pathlib import Path


logger = logging.getLogger(__name__)


# ============================================================================
# VALIDATION EXCEPTIONS
# ============================================================================

class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


class ConfigEnvironmentError(Exception):
    """Raised when environment configuration is invalid"""
    pass


# ============================================================================
# CONFIGURATION VALIDATORS
# ============================================================================

class TimeValidator:
    """Validator for time-based configuration values"""

    @staticmethod
    def validate_time_format(value: str, field_name: str = "time") -> str:
        """Validate HH:MM format

        Args:
            value: Time string in HH:MM format
            field_name: Name of field for error messages

        Returns:
            Validated time string

        Raises:
            ConfigValidationError: If format is invalid
        """
        if not isinstance(value, str):
            raise ConfigValidationError(f"{field_name} must be a string, got {type(value)}")

        try:
            parts = value.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid format")

            hours = int(parts[0])
            minutes = int(parts[1])

            if not (0 <= hours <= 23):
                raise ValueError("Hours must be 00-23")
            if not (0 <= minutes <= 59):
                raise ValueError("Minutes must be 00-59")

        except (ValueError, AttributeError) as e:
            raise ConfigValidationError(
                f"{field_name} must be in HH:MM format, got '{value}': {e}"
            )

        return f"{hours:02d}:{minutes:02d}"

    @staticmethod
    def validate_time_range(start: str, end: str) -> None:
        """Validate that end time is after start time

        Args:
            start: Start time in HH:MM format
            end: End time in HH:MM format

        Raises:
            ConfigValidationError: If end is not after start
        """
        try:
            start_h, start_m = map(int, start.split(':'))
            end_h, end_m = map(int, end.split(':'))

            start_mins = start_h * 60 + start_m
            end_mins = end_h * 60 + end_m

            if end_mins <= start_mins:
                raise ConfigValidationError(
                    f"End time {end} must be after start time {start}"
                )
        except (ValueError, AttributeError) as e:
            raise ConfigValidationError(f"Invalid time range: {e}")


class PathValidator:
    """Validator for file path configuration values"""

    @staticmethod
    def validate_path(value: str, field_name: str = "path",
                      must_exist: bool = False) -> str:
        """Validate file/directory path

        Args:
            value: Path string
            field_name: Name of field for error messages
            must_exist: If True, path must exist

        Returns:
            Validated path string

        Raises:
            ConfigValidationError: If path is invalid
        """
        if not isinstance(value, str):
            raise ConfigValidationError(f"{field_name} must be a string")

        path = Path(value)

        if must_exist and not path.exists():
            raise ConfigValidationError(f"{field_name} path does not exist: {value}")

        return str(path)


class RangeValidator:
    """Validator for numeric range configuration values"""

    @staticmethod
    def validate_range(value: Union[int, float], field_name: str = "value",
                       min_val: Optional[Union[int, float]] = None,
                       max_val: Optional[Union[int, float]] = None) -> Union[int, float]:
        """Validate numeric value is within range

        Args:
            value: Numeric value to validate
            field_name: Name of field for error messages
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)

        Returns:
            Validated value

        Raises:
            ConfigValidationError: If value is out of range
        """
        if not isinstance(value, (int, float)):
            raise ConfigValidationError(
                f"{field_name} must be numeric, got {type(value)}"
            )

        if min_val is not None and value < min_val:
            raise ConfigValidationError(
                f"{field_name} must be >= {min_val}, got {value}"
            )

        if max_val is not None and value > max_val:
            raise ConfigValidationError(
                f"{field_name} must be <= {max_val}, got {value}"
            )

        return value


class ChoiceValidator:
    """Validator for choice configuration values"""

    @staticmethod
    def validate_choice(value: str, field_name: str = "value",
                        choices: List[str] = None) -> str:
        """Validate value is in allowed choices

        Args:
            value: Value to validate
            field_name: Name of field for error messages
            choices: List of allowed values

        Returns:
            Validated value

        Raises:
            ConfigValidationError: If value not in choices
        """
        if choices is None:
            choices = []

        if value not in choices:
            raise ConfigValidationError(
                f"{field_name} must be one of {choices}, got '{value}'"
            )

        return value


# ============================================================================
# SECTION VALIDATORS
# ============================================================================

@dataclass
class WeatherConfig:
    """Weather section configuration"""
    location: str
    units: str = "metric"
    update_interval: int = 300
    display_format: str = "detailed"
    show_forecast: bool = True
    api_timeout: int = 10

    def validate(self) -> None:
        """Validate weather configuration"""
        if not isinstance(self.location, str) or not self.location:
            raise ConfigValidationError("location must be a non-empty string")

        ChoiceValidator.validate_choice(self.units, "units", ["metric", "imperial"])
        RangeValidator.validate_range(self.update_interval, "update_interval", 10, 3600)
        ChoiceValidator.validate_choice(
            self.display_format, "display_format", ["compact", "detailed"]
        )
        RangeValidator.validate_range(self.api_timeout, "api_timeout", 1, 60)


@dataclass
class MBTAConfig:
    """MBTA section configuration"""
    home_station_id: str
    home_station_name: str
    work_station_id: str
    work_station_name: str
    update_interval: int = 30
    morning_start: str = "06:00"
    morning_end: str = "12:00"
    evening_start: str = "15:00"
    evening_end: str = "21:00"
    show_delays: bool = True
    max_predictions: int = 3
    api_timeout: int = 5

    def validate(self) -> None:
        """Validate MBTA configuration"""
        required_strings = [
            self.home_station_id, self.home_station_name,
            self.work_station_id, self.work_station_name
        ]
        for s in required_strings:
            if not isinstance(s, str) or not s:
                raise ConfigValidationError("Station IDs and names must be non-empty strings")

        RangeValidator.validate_range(self.update_interval, "update_interval", 10, 600)
        TimeValidator.validate_time_format(self.morning_start, "morning_start")
        TimeValidator.validate_time_format(self.morning_end, "morning_end")
        TimeValidator.validate_time_format(self.evening_start, "evening_start")
        TimeValidator.validate_time_format(self.evening_end, "evening_end")
        TimeValidator.validate_time_range(self.morning_start, self.morning_end)
        TimeValidator.validate_time_range(self.evening_start, self.evening_end)
        RangeValidator.validate_range(self.max_predictions, "max_predictions", 1, 10)
        RangeValidator.validate_range(self.api_timeout, "api_timeout", 1, 60)


@dataclass
class DisneyConfig:
    """Disney section configuration"""
    park_id: int
    park_name: str
    update_interval: int = 10
    data_refresh_rides: int = 20
    sort_by: str = "wait_time"
    show_closed: bool = False
    favorite_rides: List[str] = field(default_factory=list)
    api_timeout: int = 5

    def validate(self) -> None:
        """Validate Disney configuration"""
        if not isinstance(self.park_id, int) or self.park_id <= 0:
            raise ConfigValidationError("park_id must be a positive integer")
        if not isinstance(self.park_name, str) or not self.park_name:
            raise ConfigValidationError("park_name must be a non-empty string")

        RangeValidator.validate_range(self.update_interval, "update_interval", 5, 600)
        RangeValidator.validate_range(self.data_refresh_rides, "data_refresh_rides", 5, 300)
        ChoiceValidator.validate_choice(self.sort_by, "sort_by", ["wait_time", "name"])

        if not isinstance(self.favorite_rides, list):
            raise ConfigValidationError("favorite_rides must be a list")

        RangeValidator.validate_range(self.api_timeout, "api_timeout", 1, 60)


@dataclass
class FlightsConfig:
    """Flights section configuration"""
    latitude: float
    longitude: float
    radius_km: float = 15.0
    update_interval: int = 15
    min_altitude: int = 0
    max_altitude: int = 10000
    show_details: bool = True
    api_timeout: int = 5

    def validate(self) -> None:
        """Validate flights configuration"""
        RangeValidator.validate_range(self.latitude, "latitude", -90, 90)
        RangeValidator.validate_range(self.longitude, "longitude", -180, 180)
        RangeValidator.validate_range(self.radius_km, "radius_km", 1, 500)
        RangeValidator.validate_range(self.update_interval, "update_interval", 5, 600)

        if self.max_altitude <= self.min_altitude:
            raise ConfigValidationError("max_altitude must be > min_altitude")

        RangeValidator.validate_range(self.api_timeout, "api_timeout", 1, 60)


@dataclass
class PomodoroConfig:
    """Pomodoro section configuration"""
    work_duration: int = 1500
    short_break: int = 300
    long_break: int = 900
    sessions_until_long_break: int = 4
    auto_start_breaks: bool = False
    auto_start_pomodoros: bool = False
    sound_enabled: bool = False

    def validate(self) -> None:
        """Validate pomodoro configuration"""
        RangeValidator.validate_range(self.work_duration, "work_duration", 60, 3600)
        RangeValidator.validate_range(self.short_break, "short_break", 30, 600)
        RangeValidator.validate_range(self.long_break, "long_break", 60, 1800)
        RangeValidator.validate_range(
            self.sessions_until_long_break, "sessions_until_long_break", 1, 20
        )


@dataclass
class MedicineConfig:
    """Medicine section configuration"""
    data_file: str
    update_interval: int = 60
    reminder_window: int = 30
    alert_upcoming_minutes: int = 15
    rotate_interval: int = 3
    enable_backups: bool = True
    backup_interval: int = 300

    def validate(self) -> None:
        """Validate medicine configuration"""
        if not isinstance(self.data_file, str) or not self.data_file:
            raise ConfigValidationError("data_file must be a non-empty string")

        RangeValidator.validate_range(self.update_interval, "update_interval", 5, 600)
        RangeValidator.validate_range(self.reminder_window, "reminder_window", 5, 120)
        RangeValidator.validate_range(
            self.alert_upcoming_minutes, "alert_upcoming_minutes", 1, 120
        )
        RangeValidator.validate_range(self.rotate_interval, "rotate_interval", 1, 10)
        RangeValidator.validate_range(self.backup_interval, "backup_interval", 30, 3600)


@dataclass
class SystemConfig:
    """System section configuration"""
    timezone: str = "America/New_York"
    display_brightness: int = 100
    auto_sleep: bool = False
    sleep_timeout: int = 300
    base_dir: str = "/home/pizero2w/pizero_apps"
    enable_metrics: bool = False
    wifi_ssid: str = ""
    wifi_password: str = ""
    hotspot_enabled: bool = False
    hotspot_ssid: str = "PiZero-Config"
    hotspot_password: str = "raspberry"

    def validate(self) -> None:
        """Validate system configuration"""
        if not isinstance(self.timezone, str) or not self.timezone:
            raise ConfigValidationError("timezone must be a non-empty string")

        RangeValidator.validate_range(self.display_brightness, "display_brightness", 0, 100)
        RangeValidator.validate_range(self.sleep_timeout, "sleep_timeout", 30, 3600)

        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ConfigValidationError("base_dir must be a non-empty string")


@dataclass
class DisplayConfig:
    """Display section configuration"""
    rotation: int = 0
    invert_colors: bool = False
    refresh_mode: str = "auto"
    partial_update_limit: int = 10
    debug_mode: bool = False

    def validate(self) -> None:
        """Validate display configuration"""
        ChoiceValidator.validate_choice(self.rotation, "rotation", [0, 90, 180, 270])
        ChoiceValidator.validate_choice(
            self.refresh_mode, "refresh_mode", ["auto", "full", "partial"]
        )
        RangeValidator.validate_range(
            self.partial_update_limit, "partial_update_limit", 1, 100
        )


# ============================================================================
# COMPLETE CONFIG VALIDATOR
# ============================================================================

class ConfigValidator:
    """Main configuration validator"""

    def __init__(self, config_path: str = None):
        """Initialize validator

        Args:
            config_path: Path to config file to validate
        """
        self.config_path = config_path
        self.config = None
        self.errors: List[str] = []

    def load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from JSON file

        Args:
            config_path: Path to config file

        Returns:
            Loaded configuration dictionary

        Raises:
            ConfigValidationError: If file cannot be read
        """
        path = config_path or self.config_path
        if not path:
            raise ConfigValidationError("Config path not specified")

        try:
            with open(path, 'r') as f:
                self.config = json.load(f)
                logger.info(f"Loaded config from {path}")
                return self.config
        except FileNotFoundError:
            raise ConfigValidationError(f"Config file not found: {path}")
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in config file: {e}")

    def validate_environment(self, environment: str = None) -> bool:
        """Validate environment value

        Args:
            environment: Environment name (development, production, test)

        Returns:
            True if valid

        Raises:
            ConfigEnvironmentError: If environment is invalid
        """
        env = environment or self.config.get('environment', 'development')

        if env not in ['development', 'production', 'test']:
            raise ConfigEnvironmentError(
                f"Invalid environment '{env}', must be one of: "
                "development, production, test"
            )

        return True

    def validate_config(self) -> bool:
        """Validate complete configuration

        Returns:
            True if validation passes

        Raises:
            ConfigValidationError: If validation fails
        """
        if not self.config:
            raise ConfigValidationError("No configuration loaded")

        self.errors = []

        try:
            # Validate environment
            self.validate_environment()

            # Validate each section
            sections = {
                'weather': WeatherConfig,
                'mbta': MBTAConfig,
                'disney': DisneyConfig,
                'flights': FlightsConfig,
                'pomodoro': PomodoroConfig,
                'medicine': MedicineConfig,
                'system': SystemConfig,
                'display': DisplayConfig,
            }

            for section_name, config_class in sections.items():
                if section_name in self.config:
                    try:
                        section_data = self.config[section_name]

                        # Create dataclass instance
                        if isinstance(section_data, dict):
                            instance = config_class(**section_data)
                            instance.validate()
                        else:
                            raise ConfigValidationError(
                                f"Section '{section_name}' must be a dictionary"
                            )
                    except TypeError as e:
                        self.errors.append(f"Section '{section_name}': {e}")
                    except ConfigValidationError as e:
                        self.errors.append(f"Section '{section_name}': {e}")

            if self.errors:
                raise ConfigValidationError(
                    f"Configuration validation failed:\n" +
                    "\n".join(f"  - {e}" for e in self.errors)
                )

            logger.info("Configuration validation passed")
            return True

        except ConfigValidationError:
            raise

    @staticmethod
    def from_file(config_path: str) -> Dict[str, Any]:
        """Load and validate config file in one call

        Args:
            config_path: Path to config file

        Returns:
            Validated configuration dictionary

        Raises:
            ConfigValidationError: If loading or validation fails
        """
        validator = ConfigValidator(config_path)
        validator.load_config()
        validator.validate_config()
        return validator.config

    def get_errors(self) -> List[str]:
        """Get list of validation errors

        Returns:
            List of error messages
        """
        return self.errors
