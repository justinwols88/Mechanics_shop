import os
import sys

# Add the parent directory to Python path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
# NOW import from config and app
from config import TestingConfig
from app import create_app
from app.extensions import db
from app.models import Mechanic, ServiceTicket, Customer

# REST OF YOUR FILE STAYS EXACTLY THE SAME...
class MechanicsTestCase(unittest.TestCase):
    """Test cases for Mechanics endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test data - FIXED: Set required fields for Customer
        self.customer = Customer()
        self.customer.email = "customer@example.com"  # Add this line
        self.customer.password = "password"           # Add this line
        
        self.mechanic = Mechanic()
        self.mechanic.email = "mechanic@example.com"
        self.mechanic.first_name = "John"             # Add required fields
        self.mechanic.last_name = "Doe"               # Add required fields
        # Set password directly to avoid unknown attribute errors
        self.mechanic.password = "mechanicpassword"
        
        self.mechanic2 = Mechanic()
        self.mechanic2.email = "jane@example.com"
        self.mechanic2.first_name = "Jane"            # Add required fields
        self.mechanic2.last_name = "Smith"            # Add required fields
        # Set password directly to avoid unknown attribute errors
        self.mechanic2.password = "password"

        db.session.add_all([self.customer, self.mechanic, self.mechanic2])
        db.session.commit()

        # Create tickets for ranking test
        self.ticket1 = ServiceTicket()
        self.ticket1.customer_id = self.customer.id
        self.ticket1.description = "Test ticket 1"    # Add description if required
        
        self.ticket2 = ServiceTicket()
        self.ticket2.customer_id = self.customer.id
        self.ticket2.description = "Test ticket 2"    # Add description if required
        
        self.ticket1.mechanics.append(self.mechanic)
        self.ticket2.mechanics.append(self.mechanic)  # Mechanic has 2 tickets
        self.ticket1.mechanics.append(self.mechanic2)  # Mechanic2 has 1 ticket

        db.session.add_all([self.ticket1, self.ticket2])
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_mechanic_login_success(self):
        """Test successful mechanic login"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)

    def test_mechanic_login_invalid_credentials(self):
        """Test mechanic login with invalid credentials (negative test)"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 401)

    def test_mechanic_registration_success(self):
        """Test successful mechanic registration"""
        response = self.client.post(
            "/mechanics/register",
            json={
                "first_name": "Bob",
                "last_name": "Wilson",
                "email": "bob@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["first_name"], "Bob")
        self.assertEqual(data["email"], "bob@example.com")

    def test_mechanic_registration_duplicate_email(self):
        """Test mechanic registration with duplicate email (negative test)"""
        response = self.client.post(
            "/mechanics/register",
            json={
                "first_name": "Duplicate",
                "last_name": "User",
                "email": "mechanic@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 409)

    def test_mechanic_registration_missing_fields(self):
        """Test mechanic registration with missing fields (negative test)"""
        response = self.client.post(
            "/mechanics/register",
            json={"first_name": "John", "email": "john@example.com"},
        )
        self.assertEqual(response.status_code, 400)

    def test_mechanics_ranking(self):
        """Test mechanics ranking by ticket count"""
        response = self.client.get("/mechanics/ranking")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("data", data)

        # Verify ranking order (mechanic should have more tickets than mechanic2)
        mechanics_data = data["data"]
        if len(mechanics_data) >= 2:
            self.assertGreaterEqual(
                mechanics_data[0]["ticket_count"], mechanics_data[1]["ticket_count"]
            )

    def test_get_mechanics_authenticated(self):
        """Test getting all mechanics with authentication"""
        # Login as mechanic first
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.get(
            "/mechanics", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("data", data)

    def test_get_mechanics_unauthenticated(self):
        """Test getting mechanics without authentication (negative test)"""
        response = self.client.get("/mechanics")
        self.assertEqual(response.status_code, 401)

    def test_get_mechanic_by_id_authenticated(self):
        """Test getting specific mechanic with authentication"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.get(
            f"/mechanics/{self.mechanic.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], self.mechanic.id)

    def test_get_mechanic_not_found(self):
        """Test getting nonexistent mechanic (negative test)"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.get(
            "/mechanics/999", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 404)

    def test_update_mechanic_authenticated(self):
        """Test updating mechanic with authentication"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.put(
            f"/mechanics/{self.mechanic.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"first_name": "Johnny", "last_name": "Doey"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["first_name"], "Johnny")

    def test_delete_mechanic_authenticated(self):
        """Test deleting mechanic with authentication"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.delete(
            f"/mechanics/{self.mechanic.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()
