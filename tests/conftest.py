"""
Pytest configuration and fixtures for handfree tests.
"""

import pytest


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require hardware)"
    )
