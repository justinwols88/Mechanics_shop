import json
import unittest
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic
from config import TestingConfig


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key"
    CACHE_TYPE = "SimpleCache"


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test data
        self.customer = Customer(email="test@example.com", password="testpassword")
        self.mechanic = Mechanic(
            first_name="John",
            last_name="Doe",
            email="mechanic@example.com",
            password="mechanicpassword",
        )
        db.session.add(self.customer)
        db.session.add(self.mechanic)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_customer_login_success(self):
        """Test successful customer login"""
        response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)

    def test_customer_login_invalid_password(self):
        """Test customer login with wrong password"""
        response = self.client.post(
            "/customers/login", json={"email": "test@example.com", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("message", data)

    def test_customer_login_nonexistent(self):
        """Test customer login with nonexistent email"""
        response = self.client.post(
            "/customers/login",
            json={"email": "nonexistent@example.com", "password": "password"},
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

    def test_mechanic_login_invalid(self):
        """Test mechanic login with invalid credentials"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get("/tickets/my-tickets")
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Token is missing")

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        response = self.client.get(
            "/tickets/my-tickets", headers={"Authorization": "Bearer invalidtoken"}
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Token is invalid")


if __name__ == "__main__":
    unittest.main()
