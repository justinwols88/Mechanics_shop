"""
Test the Flask application
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_app_creation():
    """Test that the app can be created"""
    try:
        from app import create_app
        app = create_app()
        assert app is not None
        assert app.config['TESTING'] is False  # Should use production config
    except Exception as e:
        pytest.fail(f"App creation failed: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
    except Exception as e:
        pytest.fail(f"Health endpoint test failed: {e}")

def test_blueprint_registration():
    """Test that blueprints are registered"""
    try:
        from app import create_app
        app = create_app()
        
        # Check if blueprints are registered
        assert 'auth' in app.blueprints
        assert 'customers' in app.blueprints
        assert 'mechanics' in app.blueprints
        assert 'inventory' in app.blueprints
        assert 'service_tickets' in app.blueprints
    except Exception as e:
        pytest.fail(f"Blueprint test failed: {e}")