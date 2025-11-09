"""
Flask Application Configuration
Defines configuration classes for different environments
"""

import os


class BaseConfig:
    """Base configuration with common settings"""

    # API Version
    API_VERSION = '1.0.0'

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # Database settings
    DB_PATH = os.environ.get(
        'PIZERO_MEDICINE_DB',
        '/home/pizero2w/pizero_apps/medicine.db'
    )

    # Config file path (for legacy config support)
    CONFIG_FILE = os.environ.get(
        'PIZERO_CONFIG_FILE',
        '/home/pizero2w/pizero_apps/config.json'
    )

    # Pagination defaults
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # CORS settings
    CORS_ENABLED = True
    CORS_ORIGINS = '*'

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Rate limiting (future use)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_PER_MINUTE = 60

    # Feature flags
    ENABLE_API_V1 = True
    ENABLE_API_V2 = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'

    # Use local database in development
    DB_PATH = os.environ.get(
        'PIZERO_MEDICINE_DB',
        os.path.join(os.getcwd(), 'medicine_dev.db')
    )

    # Disable rate limiting in development
    RATE_LIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Stricter settings in production
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in environment

    # Production database path
    DB_PATH = '/home/pizero2w/pizero_apps/medicine.db'

    # Enable rate limiting in production
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 60

    # Production logging
    LOG_LEVEL = 'INFO'


class TestingConfig(BaseConfig):
    """Testing configuration"""

    DEBUG = True
    TESTING = True

    # Use in-memory database for testing
    DB_PATH = ':memory:'

    # Disable CORS for testing
    CORS_ENABLED = False

    # More verbose logging in testing
    LOG_LEVEL = 'DEBUG'

    # Disable rate limiting in testing
    RATE_LIMIT_ENABLED = False


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name='development'):
    """
    Get configuration class by name

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configuration class
    """
    return config_map.get(config_name, config_map['default'])
