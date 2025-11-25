"""
Test cases for authentication endpoints
"""

import os
import sys
import json
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic


class TestAuth:
    """Test authentication endpoints"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.customer = Customer()
        self.customer.email = "test@example.com"
        self.customer.password = "testpassword"  # Set password directly
        
        self.mechanic = Mechanic()
        self.mechanic.email = "mechanic@example.com"
        self.mechanic.first_name = "John"
        self.mechanic.last_name = "Doe"
        self.mechanic.password = "mechanicpassword"  # Set password directly
        
        db.session.add(self.customer)
        db.session.add(self.mechanic)
        db.session.commit()

    def teardown_method(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_customer_login_success(self):
        """Test successful customer login"""
        response = self.client.post(
            "/customers/login",
            json={"email": "test@example.com", "password": "testpassword"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "token" in data

    def test_customer_login_invalid_password(self):
        """Test customer login with wrong password"""
        response = self.client.post(
            "/customers/login", json={"email": "test@example.com", "password": "wrong"}
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "message" in data

    def test_customer_login_nonexistent(self):
        """Test customer login with nonexistent email"""
        response = self.client.post(
            "/customers/login",
            json={"email": "nonexistent@example.com", "password": "password"},
        )
        assert response.status_code == 401

    def test_mechanic_login_success(self):
        """Test successful mechanic login"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "token" in data

    def test_mechanic_login_invalid(self):
        """Test mechanic login with invalid credentials"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get("/tickets/my-tickets")
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["message"] == "Token is missing"

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        response = self.client.get(
            "/tickets/my-tickets", headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data["message"] == "Token is invalid"


if __name__ == "__main__":
    unittest.main()
