"""
API v1 Routes Package

This package contains all route handlers for API v1.
Routes are organized by resource type (medicines, tracking, config).
"""

# Import route modules to register them with the blueprint
from . import medicines
from . import tracking
from . import config

__all__ = ['medicines', 'tracking', 'config']
