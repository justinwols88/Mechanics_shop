"""
Test setup utilities
"""
import pytest
from app import create_app, db
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from config import TestingConfig

@pytest.fixture(scope='function')
def test_app():
    """Create test application with database"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        yield app
        
        # Clean up
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    """Create test client"""
    return test_app.test_client()

@pytest.fixture(scope='function')
def test_customer(test_app):
    """Create test customer"""
    with test_app.app_context():
        customer = Customer(
            first_name="Test",
            last_name="Customer",
            email="test@example.com"
        )
        customer.set_password("password123")
        db.session.add(customer)
        db.session.commit()
        
        return customer

@pytest.fixture(scope='function')
def test_mechanic(test_app):
    """Create test mechanic"""
    with test_app.app_context():
        mechanic = Mechanic(
            first_name="Test",
            last_name="Mechanic",
            email="mechanic@example.com"
        )
        mechanic.set_password("mechanic123")
        db.session.add(mechanic)
        db.session.commit()
        
        return mechanic