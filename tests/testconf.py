"""
Pytest configuration file for Mechanics Shop API tests
"""

import os
import sys
import pytest

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic, ServiceTicket, Inventory
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def session(app):
    """Create database session"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        options = {"bind": connection, "binds": {}}
        session = db.create_scoped_session(options=options)
        
        db.session = session
        
        yield session
        
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def sample_customer(session):
    """Create a sample customer for testing"""
    customer = Customer(
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    customer.set_password("testpassword")
    session.add(customer)
    session.commit()
    return customer


@pytest.fixture
def sample_mechanic(session):
    """Create a sample mechanic for testing"""
    mechanic = Mechanic(
        first_name="John",
        last_name="Doe",
        email="mechanic@example.com",
        specialization="General"
    )
    mechanic.set_password("mechanicpassword")
    session.add(mechanic)
    session.commit()
    return mechanic


@pytest.fixture
def sample_inventory(session, sample_mechanic):
    """Create sample inventory item for testing"""
    inventory = Inventory(
        part_name="Test Part",
        part_number="TEST123",
        quantity=10,
        price=29.99,
        mechanic_id=sample_mechanic.id
    )
    session.add(inventory)
    session.commit()
    return inventory


@pytest.fixture
def sample_service_ticket(session, sample_customer, sample_mechanic):
    """Create sample service ticket for testing"""
    ticket = ServiceTicket(
        vehicle_info="Test Vehicle",
        issue_description="Test issue",
        status="open",
        customer_id=sample_customer.id,
        mechanic_id=sample_mechanic.id
    )
    session.add(ticket)
    session.commit()
    return ticket