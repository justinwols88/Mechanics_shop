"""
Pytest configuration and fixtures
"""
import pytest
from app import create_app, db
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create test data
        customer = Customer(
            first_name="Test",
            last_name="Customer",
            email="test@example.com"
        )
        customer.set_password("password123")
        db.session.add(customer)
        
        mechanic = Mechanic(
            first_name="Test",
            last_name="Mechanic", 
            email="mechanic@example.com"
        )
        mechanic.set_password("mechanic123")
        db.session.add(mechanic)
        
        inventory = Inventory(
            part_name="Test Part",
            part_number="TEST-001",
            price=29.99,
            quantity=10
        )
        db.session.add(inventory)
        
        db.session.commit()
        
        yield app
        
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()