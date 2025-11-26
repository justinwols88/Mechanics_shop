import unittest
import json
import sys
import os

# Add the parent directory to Python path FIRST
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# NOW import from config and app
from config import TestingConfig
from app import create_app
from app.extensions import db
from app.models import Customer, ServiceTicket

from flask_limiter import Limiter

# REST OF YOUR FILE STAYS THE SAME...
class CustomerTestCase(unittest.TestCase):
    """Test cases for Customer endpoints"""

    def _reset_rate_limiter(self):
        """Best-effort reset of the rate limiter without relying on Flask type hints."""
        app = self.app

        # Try getting limiter from Flask's extensions dict
        limiter = None
        if hasattr(app, "extensions"):
            limiter = app.extensions.get("limiter")

        # Fallback to attribute if present
        if limiter is None and hasattr(app, "limiter"):
            limiter = getattr(app, "limiter")

        if isinstance(limiter, Limiter) and hasattr(limiter, "reset"):
            limiter.reset()

    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test customer
        self.customer = Customer()  # was: Customer(email="test@example.com", password="testpassword")
        self.customer.email = "test@example.com"
        self.customer.password = "testpassword"
        db.session.add(self.customer)
        db.session.commit()

        # Reset rate limiter for clean test state
        self._reset_rate_limiter()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # Reset rate limiter again
        self._reset_rate_limiter()

    def test_customer_login_success(self):
        """Test successful customer login"""
        response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)
        self.assertTrue(isinstance(data["token"], str))

    def test_customer_login_invalid_password(self):
        """Test customer login with invalid password (negative test)"""
        response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("message", data)

    def test_customer_login_nonexistent_email(self):
        """Test customer login with nonexistent email (negative test)"""
        response = self.client.post(
            "/customers/login",
            json={"email": "nonexistent@example.com", "password": "password"},
        )
        self.assertEqual(response.status_code, 401)

    def test_customer_login_missing_fields(self):
        """Test customer login with missing fields (negative test)"""
        response = self.client.post(
            "/customers/login", json={"email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 400)

    def test_customer_registration_success(self):
        """Test successful customer registration"""
        response = self.client.post(
            "/customers/register",
            json={"email": "newcustomer@example.com", "password": "newpassword"},
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["email"], "newcustomer@example.com")
        self.assertIn("id", data)

    def test_customer_registration_duplicate_email(self):
        """Test customer registration with duplicate email (negative test)"""
        response = self.client.post(
            "/customers/register",
            json={"email": "test@example.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("already", data["message"].lower())

    def test_customer_registration_missing_fields(self):
        """Test customer registration with missing fields (negative test)"""
        response = self.client.post(
            "/customers/register", json={"email": "test@example.com"}
        )
        self.assertEqual(response.status_code, 400)

    def test_get_customer_by_id_success(self):
        """Test getting customer by ID"""
        response = self.client.get(f"/customers/{self.customer.id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["id"], self.customer.id)
        self.assertEqual(data["email"], self.customer.email)

    def test_get_customer_by_id_not_found(self):
        """Test getting nonexistent customer (negative test)"""
        response = self.client.get("/customers/999")
        self.assertEqual(response.status_code, 404)

    def test_update_customer_success(self):
        """Test updating customer information"""
        response = self.client.put(
            f"/customers/{self.customer.id}",
            json={"email": "updated@example.com", "password": "newpassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["email"], "updated@example.com")

    def test_update_customer_not_found(self):
        """Test updating nonexistent customer (negative test)"""
        response = self.client.put(
            "/customers/999", json={"email": "updated@example.com"}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_customer_success(self):
        """Test deleting a customer"""
        response = self.client.delete(f"/customers/{self.customer.id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("deleted", data["message"].lower())

    def test_delete_customer_not_found(self):
        """Test deleting nonexistent customer (negative test)"""
        response = self.client.delete("/customers/999")
        self.assertEqual(response.status_code, 404)

    def test_get_customers_paginated(self):
        """Test getting paginated customers list"""
        response = self.client.get("/customers/all?page=1&per_page=5")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("customers", data)
        self.assertIn("page", data)
        self.assertIn("total", data)

    def test_get_my_tickets_authenticated(self):
        """Test getting customer's tickets with authentication"""
        # First login to get token
        login_response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        token = json.loads(login_response.data)["token"]

        # Create a test ticket
        ticket = ServiceTicket()
        ticket.customer_id = self.customer.id
        db.session.add(ticket)
        db.session.commit()

        # Access protected endpoint
        response = self.client.get(
            "/customers/my-tickets", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_my_tickets_unauthenticated(self):
        """Test getting tickets without authentication (negative test)"""
        response = self.client.get("/customers/my-tickets")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
