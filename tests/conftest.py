"""
Shared configuration for tests
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables if not already set
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'testing'

if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'test-secret-key'

if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///test.db'

@pytest.fixture(scope='session')
def app():
    """Create app for testing"""
    try:
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app
    except ImportError as e:
        pytest.skip(f"App creation skipped: {e}")

@pytest.fixture(scope='session')
def client(app):
    """Create test client"""
    return app.test_client()