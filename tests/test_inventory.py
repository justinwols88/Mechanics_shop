import unittest
import json
import sys
import os
from config import TestingConfig



# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Inventory, Mechanic



class InventoryTestCase(unittest.TestCase):
    """Test cases for Inventory endpoints"""

    def setUp(self):
        """Set up test environment"""
        # Import the TestingConfig class directly
        

        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test data - use 'part_name' instead of 'name'
        self.mechanic = Mechanic(
            first_name="John",
            last_name="Doe",
            email="mechanic@example.com",
            password="mechanicpassword",
        )
        self.inventory_item = Inventory(
            part_name="Brake Pads", price=49.99
        )  # Changed 'name' to 'part_name' and 'price' to 'cost'

        db.session.add_all([self.mechanic, self.inventory_item])
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_inventory_success(self):
        """Test creating inventory item"""
        response = self.client.post(
            "/inventory/", json={"part_name": "Oil Filter", "price": 12.99}
        )

        # Debug: print the response to see what's wrong
        print(f"Status: {response.status_code}")
        print(f"Response: {response.data}")

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["part_name"], "Oil Filter")  # Update this too if needed
        self.assertEqual(data["price"], 12.99)

    def test_create_inventory_missing_fields(self):
        """Test creating inventory with missing fields (negative test)"""
        response = self.client.post("/inventory/", json={"part_name": "Test Part"})
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_invalid_price(self):
        """Test creating inventory with invalid price (negative test)"""
        response = self.client.post(
            "/inventory/", json={"part_name": "Test Part", "price": -10.00}
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_inventory(self):
        """Test getting all inventory items"""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_update_inventory_authenticated_success(self):
        """Test updating inventory item with authentication"""
        # Login as mechanic first
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.put(
            f"/inventory/{self.inventory_item.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"part_name": "Premium Brake Pads", "cost": 59.99},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["part_name"], "Premium Brake Pads")

    def test_update_inventory_unauthenticated(self):
        """Test updating inventory without authentication (negative test)"""
        response = self.client.put(
            f"/inventory/{self.inventory_item.id}",
            json={"part_name": "Updated Part", "price": 39.99},
        )
        self.assertEqual(response.status_code, 401)

    def test_update_inventory_not_found(self):
        """Test updating nonexistent inventory item (negative test)"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.put(
            "/inventory/999",
            headers={"Authorization": f"Bearer {token}"},
            json={"part_name": "Updated Part", "price": 39.99},
        )
        self.assertEqual(response.status_code, 404)

    def test_update_inventory_invalid_data(self):
        """Test updating inventory with invalid data (negative test)"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.put(
            f"/inventory/{self.inventory_item.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"price": -10.00},
        )
        self.assertEqual(response.status_code, 400)

    def test_archive_inventory_authenticated(self):
        """Test archiving inventory item with authentication"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.patch(
            f"/inventory/{self.inventory_item.id}/archive",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()
