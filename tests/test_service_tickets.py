import unittest
import json
import sys
import os
from typing import cast

from flask import config

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import ServiceTicket, Customer, Mechanic, Inventory
from config import TestingConfig


class ServiceTicketsTestCase(unittest.TestCase):
    """Test cases for Service Tickets endpoints"""

    def setUp(self):
        """Set up test environment"""
        # Import the TestingConfig class directly
        from config import TestingConfig

        self.app = create_app(TestingConfig)  # Pass the class, not a string
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test data
        self.customer = Customer(email="customer@example.com", password="password")
        self.mechanic = Mechanic(
            first_name="John",
            last_name="Doe",
            email="mechanic@example.com",
            password="mechanicpassword",
        )
        self.inventory = Inventory(part_name="Brake Pads", price=49.99)  # Use part_name
        self.ticket = ServiceTicket(
            description="Test service ticket", customer_id=1, status="open"
        )

        db.session.add_all([self.customer, self.mechanic, self.inventory, self.ticket])
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.close()  # Add this line
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_service_ticket_authenticated(self):
        """Test creating service ticket with authentication"""
        # Login as customer first
        login_response = self.client.post(
            "/customers/login",
            json={"email": "customer@example.com", "password": "password"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "customer_id": self.customer.id,
                "description": "New service request",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["description"], "New service request")

    def test_create_service_ticket_unauthenticated(self):
        """Test creating ticket without authentication (negative test)"""
        response = self.client.post(
            "/tickets", json={"customer_id": 1, "description": "New service request"}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_service_ticket_missing_fields(self):
        """Test creating ticket with missing fields (negative test)"""
        login_response = self.client.post(
            "/customers/login",
            json={"email": "customer@example.com", "password": "password"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {token}"},
            json={"customer_id": self.customer.id},
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_service_tickets_authenticated(self):
        """Test getting all service tickets with authentication"""
        login_response = self.client.post(
            "/customers/login",
            json={"email": "customer@example.com", "password": "password"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.get(
            "/tickets", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertIn("data", data)

    def test_get_service_ticket_by_id_authenticated(self):
        """Test getting specific service ticket with authentication"""
        login_response = self.client.post(
            "/customers/login",
            json={"email": "customer@example.com", "password": "password"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.get(
            f"/tickets/{self.ticket.id}", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["id"], self.ticket.id)

    def test_get_service_ticket_not_found(self):
        """Test getting nonexistent service ticket (negative test)"""
        login_response = self.client.post(
            "/customers/login",
            json={"email": "customer@example.com", "password": "password"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.get(
            "/tickets/999", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_ticket_mechanics_add(self):
        """Test adding mechanics to a ticket"""
        response = self.client.put(
            f"/tickets/{self.ticket.id}/edit", json={"add_ids": [self.mechanic.id]}
        )
        self.assertEqual(response.status_code, 200)

        # Verify mechanic was added
        updated_ticket = db.session.get(ServiceTicket, self.ticket.id)
        self.assertIsNotNone(updated_ticket)
        ticket = cast(ServiceTicket, updated_ticket)
        mechanics_list = cast("list[Mechanic]", ticket.mechanics)
        self.assertIn(self.mechanic, mechanics_list)

    def test_edit_ticket_mechanics_remove(self):
        """Test removing mechanics from a ticket"""
        # First add a mechanic
        self.ticket.mechanics.append(self.mechanic)
        db.session.commit()

        response = self.client.put(
            f"/tickets/{self.ticket.id}/edit", json={"remove_ids": [self.mechanic.id]}
        )
        self.assertEqual(response.status_code, 200)

        # Verify mechanic was removed
        updated_ticket = db.session.get(ServiceTicket, self.ticket.id)
        self.assertIsNotNone(updated_ticket)
        ticket = cast(ServiceTicket, updated_ticket)
        mechanics_list = cast("list[Mechanic]", ticket.mechanics)
        self.assertNotIn(self.mechanic, mechanics_list)

    def test_edit_ticket_not_found(self):
        """Test editing nonexistent ticket (negative test)"""
        response = self.client.put("/tickets/999/edit", json={"add_ids": [1]})
        self.assertEqual(response.status_code, 404)

    def test_add_part_to_ticket_success(self):
        """Test adding inventory part to a ticket"""
        response = self.client.post(
            f"/tickets/{self.ticket.id}/add-part", json={"part_id": self.inventory.id}
        )
        self.assertEqual(response.status_code, 200)

        # Verify part was added
        updated_ticket = db.session.get(ServiceTicket, self.ticket.id)
        self.assertIsNotNone(updated_ticket)
        ticket = cast(ServiceTicket, updated_ticket)
        # Tell the type checker that this is a collection of Inventory
        inventory_items = cast("list[Inventory]", ticket.inventory)
        self.assertIn(self.inventory, inventory_items)

    def test_add_part_to_ticket_ticket_not_found(self):
        """Test adding part to nonexistent ticket (negative test)"""
        response = self.client.post(
            "/tickets/999/add-part", json={"part_id": self.inventory.id}
        )
        self.assertEqual(response.status_code, 404)

    def test_add_part_to_ticket_part_not_found(self):
        """Test adding nonexistent part to ticket (negative test)"""
        response = self.client.post(
            f"/tickets/{self.ticket.id}/add-part", json={"part_id": 999}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_service_ticket_authenticated(self):
        """Test deleting service ticket with mechanic authentication"""
        # Login as mechanic first
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.delete(
            f"/tickets/{self.ticket.id}", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

    def test_delete_service_ticket_not_found(self):
        """Test deleting nonexistent service ticket (negative test)"""
        login_response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic@example.com", "password": "mechanicpassword"},
        )
        token = json.loads(login_response.data)["token"]

        response = self.client.delete(
            "/tickets/999", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
