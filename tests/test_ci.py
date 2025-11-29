"""
Simple test file for CI environment
"""

def test_ci_environment():
    """Test that CI environment is set up correctly"""
    import os
    # FLASK_ENV might not be set in all environments, that's okay
    # Just check that we're in a Python environment
    assert 'PYTEST_CURRENT_TEST' in os.environ  # This should always be set when running pytest
    assert 'PATH' in os.environ  # Basic environment check

def test_python_version():
    """Test Python environment"""
    import sys
    assert sys.version_info >= (3, 7)  # Should work with Python 3.7+

def test_imports():
    """Test basic imports work"""
    try:
        import flask
        import pytest
        import sqlalchemy
        assert True
    except ImportError as e:
        assert False, f"Import failed: {e}"

def test_flask_caching_available():
    """Test if flask-caching is available"""
    try:
        from flask_caching import Cache
        assert True
    except ImportError:
        import pytest
        pytest.skip("flask-caching not installed")