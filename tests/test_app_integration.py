"""
Integration tests for Mechanics Shop API - Fixed Version
"""
import pytest
from app import create_app
from config import TestingConfig

def test_health_endpoint():
    """Test health endpoint returns correct structure"""
    app = create_app(TestingConfig)
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        # Updated assertion to match actual response structure
        assert 'status' in data
        assert 'timestamp' in data
        assert 'services' in data
        assert data['status'] == 'healthy'
        assert data['services']['database'] == 'healthy'
        assert data['services']['api'] == 'healthy'

def test_blueprint_endpoints():
    """Test blueprint endpoints are properly registered"""
    app = create_app(TestingConfig)
    with app.test_client() as client:
        # Test auth endpoints
        response = client.post('/auth/customer/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        # Should get 400 (bad request) or 401 (unauthorized), not 308 redirect
        assert response.status_code in [400, 401]
        
        # Test customers endpoint
        response = client.get('/customers/')
        # Should get 401 (unauthorized) since no token provided
        assert response.status_code == 401
        
        # Test mechanics endpoint  
        response = client.get('/mechanics/')
        # Should be accessible without auth
        assert response.status_code == 200

def test_app_config():
    """Test application configuration"""
    app = create_app(TestingConfig)
    assert app.config['TESTING'] == True
    assert 'sqlite://' in app.config['SQLALCHEMY_DATABASE_URI']

def test_database_connection():
    """Test database connection and model operations"""
    app = create_app(TestingConfig)
    with app.app_context():
        from app import db
        from app.models.customer import Customer
        
        # Create a test customer
        customer = Customer(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        customer.set_password("password123")
        
        db.session.add(customer)
        db.session.commit()
        
        # Verify we can retrieve the customer
        retrieved = Customer.query.filter_by(email="test@example.com").first()
        assert retrieved is not None
        assert retrieved.first_name == "Test"
        assert retrieved.check_password("password123")

def test_production_config():
    """Test production configuration"""
    from config import ProductionConfig
    app = create_app(ProductionConfig)
    assert app.config['DEBUG'] == False
    assert app.config['TESTING'] == False