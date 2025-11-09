"""
Shared Application Utilities
Common functions used across all Pi Zero 2W display applications
"""

import os
import sys
import time
import logging
import threading
import signal
from contextlib import contextmanager
from typing import Callable, Optional


# ============================================================================
# PATH MANAGEMENT
# ============================================================================

def get_base_dir() -> str:
    """Get base directory for applications

    Uses environment variable PIZERO_BASE_DIR if set, otherwise uses default
    """
    return os.environ.get('PIZERO_BASE_DIR', '/home/pizero2w/pizero_apps')


def get_pic_dir() -> str:
    """Get directory for display pictures/icons"""
    base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(base, 'python/pic/2in13')


def get_font_dir() -> str:
    """Get directory for fonts"""
    base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(base, 'python/pic')


def get_lib_dir() -> str:
    """Get directory for Python libraries"""
    base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(base, 'python/lib')


def setup_paths():
    """Add library path to sys.path (call this at app startup)"""
    lib_dir = get_lib_dir()
    if lib_dir not in sys.path:
        sys.path.append(lib_dir)


# ============================================================================
# LOGGING
# ============================================================================

def setup_logging(app_name: str, log_to_file: bool = True, level=logging.INFO) -> logging.Logger:
    """Setup standardized logging for application

    Args:
        app_name: Name of the application (used in log messages and filename)
        log_to_file: If True, logs to /tmp/{app_name}.log
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    handlers = [logging.StreamHandler()]

    if log_to_file:
        log_path = f'/tmp/{app_name}.log'
        handlers.append(logging.FileHandler(log_path))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    logger = logging.getLogger(app_name)
    return logger


# ============================================================================
# EXIT HANDLING
# ============================================================================

def check_exit_requested(gt_dev) -> bool:
    """Check if exit has been requested by menu

    Args:
        gt_dev: Touch device object

    Returns:
        True if exit requested, False otherwise
    """
    return hasattr(gt_dev, "exit_requested") and gt_dev.exit_requested


def cleanup_touch_state(gt_old):
    """Reset touch state to clean values

    Args:
        gt_old: Previous touch state object
    """
    gt_old.X[0] = 0
    gt_old.Y[0] = 0
    gt_old.S[0] = 0


def install_signal_handlers(cleanup_callback: Callable):
    """Install signal handlers for graceful shutdown

    Args:
        cleanup_callback: Function to call on SIGTERM/SIGINT

    Example:
        def cleanup():
            epd.sleep()
            epd.module_exit()

        install_signal_handlers(cleanup)
    """
    def signal_handler(signum, frame):
        logging.info(f"Received signal {signum}, shutting down gracefully")
        cleanup_callback()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


# ============================================================================
# THREADING
# ============================================================================

class TouchThread:
    """Reusable touch detection thread

    Handles GPIO/touch interrupt polling in background thread
    """

    def __init__(self, gt, gt_dev, interval: float = 0.01):
        """Initialize touch thread

        Args:
            gt: Touch driver interface
            gt_dev: Touch device state object
            interval: Polling interval in seconds (default: 10ms)
        """
        self.gt = gt
        self.gt_dev = gt_dev
        self.interval = interval
        self.running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start touch detection thread"""
        if self.running:
            return

        self.running = True
        self._thread = threading.Thread(target=self._irq_loop, daemon=True)
        self._thread.start()
        logging.debug("Touch detection thread started")

    def stop(self):
        """Stop touch detection thread"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        logging.debug("Touch detection thread stopped")

    def _irq_loop(self):
        """Internal IRQ polling loop"""
        while self.running:
            try:
                if self.gt.digital_read(self.gt.INT) == 0:
                    self.gt_dev.Touch = 1
                else:
                    self.gt_dev.Touch = 0
            except Exception as e:
                logging.error(f"Touch detection error: {e}")

            time.sleep(self.interval)


@contextmanager
def touch_thread_context(gt, gt_dev, interval: float = 0.01):
    """Context manager for touch detection thread

    Usage:
        with touch_thread_context(gt, gt_dev):
            # Your app code here
            # Thread automatically stops on exit
    """
    thread = TouchThread(gt, gt_dev, interval)
    thread.start()
    try:
        yield thread
    finally:
        thread.stop()


# ============================================================================
# FONT CACHING
# ============================================================================

_font_cache = {}


def get_font(name: str, size: int):
    """Get font with caching to avoid repeated disk loads

    Args:
        name: Font name (e.g., 'Roboto-Bold', 'Roboto-Regular')
        size: Font size in points

    Returns:
        PIL ImageFont object
    """
    from PIL import ImageFont

    key = (name, size)
    if key not in _font_cache:
        font_path = os.path.join(get_font_dir(), f"{name}.ttf")
        _font_cache[key] = ImageFont.truetype(font_path, size)

    return _font_cache[key]


def clear_font_cache():
    """Clear font cache (useful for testing/debugging)"""
    global _font_cache
    _font_cache.clear()


# ============================================================================
# CONFIGURATION
# ============================================================================

class ConfigLoader:
    """Thread-safe configuration loader with environment variable support

    Supports loading environment-specific configurations:
    - PIZERO_ENV: Set to 'development', 'production', or 'test'
    - PIZERO_CONFIG: Override config file path
    - PIZERO_CONFIG_DIR: Override config directory
    """

    _instance = None
    _config = None
    _environment = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_environment(cls) -> str:
        """Get current environment

        Returns:
            Environment name: 'development', 'production', or 'test'
        """
        if cls._environment is None:
            cls._environment = os.environ.get('PIZERO_ENV', 'development')
        return cls._environment

    @classmethod
    def set_environment(cls, environment: str) -> None:
        """Set environment and reload config

        Args:
            environment: Environment name ('development', 'production', 'test')
        """
        if environment not in ['development', 'production', 'test']:
            raise ValueError(f"Invalid environment: {environment}")

        cls._environment = environment
        cls._config = None  # Force reload

    @classmethod
    def get_config_path(cls) -> str:
        """Get path to config.json

        Checks for config file in this order:
        1. PIZERO_CONFIG environment variable
        2. Environment-specific config in config/ directory
        3. Legacy config.json in base directory
        4. Environment-specific config in current directory

        Returns:
            Path to configuration file
        """
        # Check explicit override
        if 'PIZERO_CONFIG' in os.environ:
            return os.environ['PIZERO_CONFIG']

        environment = cls.get_environment()
        config_dir = os.environ.get(
            'PIZERO_CONFIG_DIR',
            os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'config')
        )

        # Try environment-specific config in config/ directory
        env_config = os.path.join(config_dir, f'{environment}.json')
        if os.path.exists(env_config):
            return env_config

        # Fall back to legacy config.json in base directory
        legacy_config = os.path.join(get_base_dir(), 'config.json')
        if os.path.exists(legacy_config):
            logging.debug(f"Using legacy config: {legacy_config}")
            return legacy_config

        # Final fallback
        return env_config

    @classmethod
    def load(cls, force_reload: bool = False) -> dict:
        """Load configuration from JSON file

        Args:
            force_reload: If True, reloads from disk even if cached

        Returns:
            Configuration dictionary
        """
        if cls._config is None or force_reload:
            import json

            config_path = cls.get_config_path()

            try:
                with open(config_path, 'r') as f:
                    cls._config = json.load(f)
                logging.debug(f"Loaded config from: {config_path}")

                # Merge with environment-specific overrides
                cls._apply_env_overrides()

            except FileNotFoundError:
                logging.error(f"Config file not found: {config_path}")
                cls._config = {}
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in config file: {e}")
                cls._config = {}

        return cls._config

    @classmethod
    def _apply_env_overrides(cls) -> None:
        """Apply environment variable overrides to loaded config

        Supports dotted notation: PIZERO_CONFIG_SECTION_KEY=value
        Example: PIZERO_CONFIG_MEDICINE_UPDATE_INTERVAL=120
        """
        if not cls._config:
            return

        for key, value in os.environ.items():
            if not key.startswith('PIZERO_CONFIG_'):
                continue

            # Remove prefix and convert to lowercase
            config_key = key[14:].lower()

            # Parse dotted notation: section_key or section_subkey
            parts = config_key.split('_', 1)
            if len(parts) != 2:
                continue

            section, key_path = parts
            section = section.lower()

            if section not in cls._config:
                continue

            # Try to convert value to appropriate type
            try:
                converted_value = cls._convert_env_value(value)
                cls._config[section][key_path] = converted_value
                logging.debug(
                    f"Applied override: {section}.{key_path} = {converted_value}"
                )
            except Exception as e:
                logging.warning(f"Failed to apply override {key}={value}: {e}")

    @staticmethod
    def _convert_env_value(value: str):
        """Convert environment variable string to appropriate type

        Args:
            value: String value from environment variable

        Returns:
            Converted value (int, float, bool, or str)
        """
        # Try boolean
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    @classmethod
    def get_section(cls, section: str, default: dict = None) -> dict:
        """Get a configuration section

        Args:
            section: Section name (e.g., 'medicine', 'weather')
            default: Default value if section not found

        Returns:
            Configuration section dictionary
        """
        config = cls.load()
        return config.get(section, default or {})

    @classmethod
    def get_value(cls, section: str, key: str, default=None):
        """Get a specific configuration value

        Args:
            section: Section name
            key: Key within section
            default: Default value if not found

        Returns:
            Configuration value
        """
        section_config = cls.get_section(section)
        return section_config.get(key, default)

    @classmethod
    def get_value_nested(cls, path: str, default=None):
        """Get a nested configuration value using dot notation

        Args:
            path: Dot-separated path (e.g., 'medicine.update_interval')
            default: Default value if not found

        Returns:
            Configuration value

        Example:
            ConfigLoader.get_value_nested('medicine.update_interval', 60)
        """
        config = cls.load()
        parts = path.split('.')

        value = config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default

        return value if value is not None else default

    @classmethod
    def validate(cls) -> bool:
        """Validate loaded configuration

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            from shared.config_validator import ConfigValidator
            config = cls.load()

            # Get config path
            config_path = cls.get_config_path()

            # Create validator and validate
            validator = ConfigValidator(config_path)
            validator.config = config
            validator.validate_config()

            return True
        except ImportError:
            logging.warning("config_validator module not available, skipping validation")
            return True
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
            raise


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def init_display_full(epd):
    """Initialize display for full update

    Args:
        epd: Display driver object
    """
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)


def init_display_partial(epd):
    """Initialize display for partial update

    Args:
        epd: Display driver object
    """
    epd.init(epd.PART_UPDATE)


def cleanup_display(epd):
    """Clean up display resources

    Args:
        epd: Display driver object
    """
    try:
        epd.sleep()
        epd.module_exit()
    except Exception as e:
        logging.error(f"Display cleanup error: {e}")


# ============================================================================
# TIMING HELPERS
# ============================================================================

class PeriodicTimer:
    """Helper for periodic operations"""

    def __init__(self, interval: float):
        """Initialize timer

        Args:
            interval: Time interval in seconds
        """
        self.interval = interval
        self.last_time = time.time()

    def is_ready(self) -> bool:
        """Check if interval has elapsed

        Returns:
            True if ready, False otherwise
        """
        current_time = time.time()
        if current_time - self.last_time >= self.interval:
            self.last_time = current_time
            return True
        return False

    def reset(self):
        """Reset timer to current time"""
        self.last_time = time.time()


# ============================================================================
# ERROR HANDLING
# ============================================================================

def safe_execute(func: Callable, error_message: str = "Operation failed", default=None):
    """Execute function with error handling

    Args:
        func: Function to execute
        error_message: Message to log on error
        default: Default value to return on error

    Returns:
        Function result or default on error
    """
    try:
        return func()
    except Exception as e:
        logging.error(f"{error_message}: {e}")
        return default


# ============================================================================
# FILE OPERATIONS
# ============================================================================

@contextmanager
def atomic_write(filepath: str):
    """Context manager for atomic file writes

    Writes to temp file then atomically renames to target

    Usage:
        with atomic_write('/path/to/file.json') as f:
            json.dump(data, f)
    """
    import tempfile

    dir_path = os.path.dirname(filepath)
    fd, temp_path = tempfile.mkstemp(dir=dir_path, prefix='.tmp_')

    try:
        with os.fdopen(fd, 'w') as f:
            yield f

        # Atomic rename
        os.replace(temp_path, filepath)

    except Exception:
        # Clean up temp file on error
        try:
            os.remove(temp_path)
        except BaseException:
            pass
        raise
