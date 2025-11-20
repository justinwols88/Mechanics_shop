import pytest
from app import create_app
from app.extensions import db as _db
from app.models import Mechanic, Customer, Inventory, ServiceTicket
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    _app = create_app(TestingConfig)
    _app.config["TESTING"] = True
    _app.config["WTF_CSRF_ENABLED"] = False

    with _app.app_context():
        yield _app


@pytest.fixture(scope="session")
def db(app):
    """Create database for the tests."""
    with app.app_context():
        _db.create_all()

    yield _db

    with app.app_context():
        _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app, db, session):
    """Create test client."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_customer(session):
    """Create a sample customer for testing."""
    customer = Customer(email="test@example.com", password="testpassword")
    session.add(customer)
    session.commit()
    return customer


@pytest.fixture
def sample_mechanic(session):
    """Create a sample mechanic for testing."""
    mechanic = Mechanic(password="mechanicpassword")
    session.add(mechanic)
    session.commit()
    return mechanic


@pytest.fixture
def sample_inventory(session):
    """Create sample inventory items for testing."""
    parts = [
        Inventory(name="Brake Pads", price=49.99),
        Inventory(name="Oil Filter", price=12.99),
        Inventory(name="Spark Plug", price=8.99),
    ]
    session.add_all(parts)
    session.commit()
    return parts


@pytest.fixture
def sample_ticket(session, sample_customer):
    """Create a sample service ticket for testing."""
    ticket = ServiceTicket(
        description="Test service ticket", customer_id=sample_customer.id, status="open"
    )
    session.add(ticket)
    session.commit()
    return ticket
