"""
Display Tests Configuration
============================

Pytest configuration for display module tests.
Sets up fixtures and configuration for testing display components.
"""

import pytest
import os
from PIL import Image, ImageDraw


@pytest.fixture
def test_canvas():
    """Provide a test canvas for tests"""
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)
    return img, draw


@pytest.fixture
def display_dimensions():
    """Provide standard display dimensions"""
    return {
        'width': 250,
        'height': 122,
        'mode': '1',
        'background_white': 255,
        'background_black': 0
    }


@pytest.fixture
def mock_font(tmp_path):
    """Create a mock font file for testing (if needed)"""
    # Return path to tmp directory that could contain fonts
    return tmp_path


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment"""
    # Clear any cached fonts before tests
    try:
        from display import fonts
        fonts.clear_font_cache()
    except:
        pass


def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "thread_safety: marks tests for thread safety"
    )
    config.addinivalue_line(
        "markers", "performance: marks performance tests"
    )
    config.addinivalue_line(
        "markers", "visual: marks visual regression tests"
    )
