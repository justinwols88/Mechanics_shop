"""
Pytest configuration file for Mechanics Shop API tests
"""

import os
import sys
import pytest

# DEBUG: Print current working directory and files
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Add the project root to Python path - ABSOLUTE PATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

print(f"Python path: {sys.path}")
print(f"Project root: {project_root}")

# Check if app directory exists
app_dir = os.path.join(project_root, 'app')
print(f"App directory exists: {os.path.exists(app_dir)}")
if os.path.exists(app_dir):
    print(f"App directory contents: {os.listdir(app_dir)}")

try:
    from app import create_app
    print("✓ Successfully imported create_app from app")
except ImportError as e:
    print(f"✗ Failed to import create_app: {e}")
    # Try alternative import
    try:
        import app
        print("✓ Successfully imported app module")
        from app import create_app
        print("✓ Successfully imported create_app after importing app")
    except ImportError as e2:
        print(f"✗ Alternative import also failed: {e2}")
    raise

try:
    from app.extensions import db
    print("✓ Successfully imported db from app.extensions")
except ImportError as e:
    print(f"✗ Failed to import db: {e}")
    raise

try:
    from app.models import Customer, Mechanic, ServiceTicket, Inventory
    print("✓ Successfully imported models")
except ImportError as e:
    print(f"✗ Failed to import models: {e}")
    raise

try:
    from config import TestingConfig
    print("✓ Successfully imported TestingConfig from config")
except ImportError as e:
    print(f"✗ Failed to import TestingConfig: {e}")
    raise

print("✓ All imports successful!")


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