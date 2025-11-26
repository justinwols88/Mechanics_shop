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
    # Prepare only supported fields
    customer_kwargs = {}
    if hasattr(Customer, "first_name"):
        customer_kwargs["first_name"] = "Test"
    if hasattr(Customer, "last_name"):
        customer_kwargs["last_name"] = "User"
    # Fallbacks if the model uses a single name field
    if not customer_kwargs.get("first_name"):
        if hasattr(Customer, "name"):
            customer_kwargs["name"] = "Test User"
        elif hasattr(Customer, "full_name"):
            customer_kwargs["full_name"] = "Test User"
    if hasattr(Customer, "email"):
        customer_kwargs["email"] = "test@example.com"

    customer = Customer(**customer_kwargs)

    # Safely set password if supported
    setter = getattr(customer, "set_password", None)
    if callable(setter):
        setter("testpassword")
    elif hasattr(customer, "password"):
        customer.password = "testpassword"

    session.add(customer)
    session.commit()
    return customer


@pytest.fixture
def sample_mechanic(session):
    """Create a sample mechanic for testing"""
    mechanic_kwargs = {}
    # Prefer separate name fields if they exist
    if hasattr(Mechanic, "first_name"):
        mechanic_kwargs["first_name"] = "John"
    if hasattr(Mechanic, "last_name"):
        mechanic_kwargs["last_name"] = "Doe"
    # Fallbacks to single name field
    if not mechanic_kwargs.get("first_name"):
        if hasattr(Mechanic, "name"):
            mechanic_kwargs["name"] = "John Doe"
        elif hasattr(Mechanic, "full_name"):
            mechanic_kwargs["full_name"] = "John Doe"
    # Optional fields
    if hasattr(Mechanic, "email"):
        mechanic_kwargs["email"] = "mechanic@example.com"
    if hasattr(Mechanic, "specialization"):
        mechanic_kwargs["specialization"] = "General"

    mechanic = Mechanic(**mechanic_kwargs)

    # Safely set password if supported
    setter = getattr(mechanic, "set_password", None)
    if callable(setter):
        setter("mechanicpassword")
    elif hasattr(mechanic, "password"):
        mechanic.password = "mechanicpassword"

    session.add(mechanic)
    session.commit()
    return mechanic


@pytest.fixture
def sample_inventory(session, sample_mechanic):
    """Create sample inventory item for testing"""
    inv_kwargs = {}

    # Name-like field
    if hasattr(Inventory, "part_name"):
        inv_kwargs["part_name"] = "Test Part"
    elif hasattr(Inventory, "name"):
        inv_kwargs["name"] = "Test Part"
    elif hasattr(Inventory, "item_name"):
        inv_kwargs["item_name"] = "Test Part"

    # Part number-like field
    if hasattr(Inventory, "part_number"):
        inv_kwargs["part_number"] = "TEST123"
    elif hasattr(Inventory, "sku"):
        inv_kwargs["sku"] = "TEST123"
    elif hasattr(Inventory, "number"):
        inv_kwargs["number"] = "TEST123"
    elif hasattr(Inventory, "code"):
        inv_kwargs["code"] = "TEST123"
    elif hasattr(Inventory, "part_no"):
        inv_kwargs["part_no"] = "TEST123"

    # Quantity-like field
    if hasattr(Inventory, "quantity"):
        inv_kwargs["quantity"] = 10
    elif hasattr(Inventory, "qty"):
        inv_kwargs["qty"] = 10
    elif hasattr(Inventory, "stock"):
        inv_kwargs["stock"] = 10

    # Price-like field
    if hasattr(Inventory, "price"):
        inv_kwargs["price"] = 29.99
    elif hasattr(Inventory, "unit_price"):
        inv_kwargs["unit_price"] = 29.99
    elif hasattr(Inventory, "cost"):
        inv_kwargs["cost"] = 29.99

    # Mechanic association
    if hasattr(Inventory, "mechanic_id"):
        inv_kwargs["mechanic_id"] = sample_mechanic.id
    elif hasattr(Inventory, "mechanic"):
        inv_kwargs["mechanic"] = sample_mechanic

    inventory = Inventory(**inv_kwargs)
    session.add(inventory)
    session.commit()
    return inventory


@pytest.fixture
def sample_service_ticket(session, sample_customer, sample_mechanic):
    """Create sample service ticket for testing"""
    ticket_kwargs = {}

    # Vehicle-related field
    if hasattr(ServiceTicket, "vehicle_info"):
        ticket_kwargs["vehicle_info"] = "Test Vehicle"
    elif hasattr(ServiceTicket, "vehicle"):
        ticket_kwargs["vehicle"] = "Test Vehicle"
    elif hasattr(ServiceTicket, "vehicle_details"):
        ticket_kwargs["vehicle_details"] = "Test Vehicle"

    # Issue/description-related field
    if hasattr(ServiceTicket, "issue_description"):
        ticket_kwargs["issue_description"] = "Test issue"
    elif hasattr(ServiceTicket, "issue"):
        ticket_kwargs["issue"] = "Test issue"
    elif hasattr(ServiceTicket, "description"):
        ticket_kwargs["description"] = "Test issue"
    elif hasattr(ServiceTicket, "problem_description"):
        ticket_kwargs["problem_description"] = "Test issue"
    elif hasattr(ServiceTicket, "service_description"):
        ticket_kwargs["service_description"] = "Test issue"
    elif hasattr(ServiceTicket, "details"):
        ticket_kwargs["details"] = "Test issue"

    # Status/state
    if hasattr(ServiceTicket, "status"):
        ticket_kwargs["status"] = "open"
    elif hasattr(ServiceTicket, "state"):
        ticket_kwargs["state"] = "open"

    # Associations
    if hasattr(ServiceTicket, "customer_id"):
        ticket_kwargs["customer_id"] = sample_customer.id
    elif hasattr(ServiceTicket, "customer"):
        ticket_kwargs["customer"] = sample_customer

    if hasattr(ServiceTicket, "mechanic_id"):
        ticket_kwargs["mechanic_id"] = sample_mechanic.id
    elif hasattr(ServiceTicket, "mechanic"):
        ticket_kwargs["mechanic"] = sample_mechanic

    ticket = ServiceTicket(**ticket_kwargs)
    session.add(ticket)
    session.commit()
    return ticket