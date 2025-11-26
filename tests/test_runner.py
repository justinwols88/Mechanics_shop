import json
import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic, ServiceTicket, Inventory


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key"
    CACHE_TYPE = "SimpleCache"


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        self.setup_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def setup_test_data(self):
        """Create initial test data"""
        # Create test customer via API to match model constructor
        self.client.post(
            "/customers/register",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        self.customer = Customer.query.filter_by(email="test@example.com").first()
        assert self.customer is not None, "Customer should be created in setup_test_data"

        # Create test mechanic via API to match model constructor
        self.client.post(
            "/mechanics/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "mechanic@example.com",
                "password": "mechanicpassword",
            },
        )
        self.mechanic = Mechanic.query.filter_by(email="mechanic@example.com").first()
        assert self.mechanic is not None, "Mechanic should be created in setup_test_data"

        # Create test inventory via API to avoid constructor arg mismatch
        inv_resp = self.client.post("/inventory/", json={"name": "Brake Pads", "price": 49.99})
        assert inv_resp.status_code in (200, 201), "Inventory creation failed in setup_test_data"
        self.inventory = Inventory.query.filter_by(name="Brake Pads").first()
        assert self.inventory is not None, "Inventory should be created in setup_test_data"

        # Create test service ticket
        self.ticket = ServiceTicket()
        # Set fields not accepted by constructor
        self.ticket.status = "open"
        self.ticket.customer_id = self.customer.id
        self.ticket.description = "Test service ticket"
        db.session.add(self.ticket)

        db.session.commit()

    def get_customer_token(self):
        """Get authentication token for test customer"""
        response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        data = json.loads(response.data)
        return data.get("token")

    def get_mechanic_token(self):
        """Get authentication token for test mechanic"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        data = json.loads(response.data)
        return data.get("token")


class AuthTestCase(BaseTestCase):
    """Test authentication endpoints"""

    def test_customer_login_success(self):
        """Test successful customer login"""
        response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)

    def test_customer_login_invalid(self):
        """Test customer login with invalid credentials"""
        response = self.client.post(
            "/customers/login", json={"email": "test@example.com", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 401)

    def test_mechanic_login_success(self):
        """Test successful mechanic login"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)


class CustomerTestCase(BaseTestCase):
    """Test customer endpoints"""

    def test_get_customers_paginated(self):
        """Test getting paginated customers"""
        response = self.client.get("/customers/all?page=1&per_page=5")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("customers", data)
        self.assertIn("page", data)

    def test_customer_registration(self):
        """Test customer registration"""
        response = self.client.post(
            "/customers/register",
            json={"email": "new@example.com", "password": "newpass"},
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["email"], "new@example.com")

    def test_get_my_tickets_authenticated(self):
        """Test getting customer tickets with auth"""
        token = self.get_customer_token()
        response = self.client.get(
            "/customers/my-tickets", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)


class MechanicTestCase(BaseTestCase):
    """Test mechanic endpoints"""

    def test_mechanics_ranking(self):
        """Test mechanics ranking"""
        response = self.client.get("/mechanics/ranking")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("data", data)

    def test_mechanic_registration(self):
        """Test mechanic registration"""
        response = self.client.post(
            "/mechanics/register",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 201)


class ServiceTicketTestCase(BaseTestCase):
    """Test service ticket endpoints"""

    def test_create_ticket_authenticated(self):
        """Test creating service ticket with auth"""
        token = self.get_customer_token()
        assert self.customer is not None, "Customer should be initialized in setUp"
        response = self.client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "customer_id": self.customer.id,
                "description": "New ticket",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_add_part_to_ticket(self):
        """Test adding part to ticket"""
        response = self.client.post(
            f"/tickets/{self.ticket.id}/add-part", json={"part_id": self.inventory.id}
        )
        self.assertEqual(response.status_code, 200)


class InventoryTestCase(BaseTestCase):
    """Test inventory endpoints"""

    def test_create_inventory(self):
        """Test creating inventory item"""
        response = self.client.post(
            "/inventory/", json={"name": "Test Part", "price": 29.99}
        )
        self.assertEqual(response.status_code, 201)

    def test_get_all_inventory(self):
        """Test getting all inventory"""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_update_inventory_authenticated(self):
        """Test updating inventory with auth"""
        token = self.get_mechanic_token()
        response = self.client.put(
            f"/inventory/{self.inventory.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Part", "price": 39.99},
        )
        self.assertEqual(response.status_code, 200)


class SystemTestCase(BaseTestCase):
    """Test system endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
