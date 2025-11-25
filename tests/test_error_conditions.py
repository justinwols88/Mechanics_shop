import unittest
import json
import sys
import os


# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Customer, Mechanic, ServiceTicket, Inventory



class ErrorConditionsTestCase(unittest.TestCase):
    """
    Comprehensive error condition testing for all API endpoints
    Tests 400 (Bad Request), 401 (Unauthorized), 404 (Not Found), and 409 (Conflict) responses
    """

    def setUp(self):
        """Set up test environment with proper isolation"""
        # Import the TestingConfig class directly
        

        # Pass the config class name as a string to match create_app signature
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create fresh database for each test
        db.create_all()

        # Create test data
        self.setup_test_data()

        # Store tokens for authenticated tests
        self.customer_token = self.get_customer_token()
        self.mechanic_token = self.get_mechanic_token()

    def tearDown(self):
        """Clean up after each test - proper teardown"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def setup_test_data(self):
        """Create comprehensive test data for error testing"""
        # Customers
        self.customer1 = Customer(email="customer1@example.com", password="password123")
        self.customer2 = Customer(email="customer2@example.com", password="password123")

        # Mechanics
        self.mechanic1 = Mechanic(
            first_name="John",
            last_name="Doe",
            email="mechanic1@example.com",
            password="mechanic123",
        )
        self.mechanic2 = Mechanic(
            first_name="Jane",
            last_name="Smith",
            email="mechanic2@example.com",
            password="mechanic123",
        )

        # Inventory - Use the correct field names based on your actual schema
        # If your database has 'part_name' instead of 'name', use that
        self.inventory1 = Inventory(
            part_name="Brake Pads", price=49.99
        )  # Changed from 'name'
        self.inventory2 = Inventory(
            part_name="Oil Filter", price=12.99
        )  # Changed from 'name'

        # Service Tickets
        self.ticket1 = ServiceTicket(
            description="Brake repair needed", customer_id=1, status="open"
        )
        self.ticket2 = ServiceTicket(
            description="Oil change requested", customer_id=1, status="in_progress"
        )

        # Add all to session and commit
        db.session.add_all(
            [
                self.customer1,
                self.customer2,
                self.mechanic1,
                self.mechanic2,
                self.inventory1,
                self.inventory2,
                self.ticket1,
                self.ticket2,
            ]
        )
        db.session.commit()

        # Set up relationships
        self.ticket1.mechanics.append(self.mechanic1)
        self.ticket1.inventory.append(self.inventory1)
        db.session.commit()

    def get_customer_token(self):
        """Get JWT token for customer authentication"""
        response = self.client.post(
            "/customers/login",
            json={"email": "customer1@example.com", "password": "password123"},
        )
        return json.loads(response.data)["token"]

    def get_mechanic_token(self):
        """Get JWT token for mechanic authentication"""
        response = self.client.post(
            "/mechanics/login",
            json={"email": "mechanic1@example.com", "password": "mechanic123"},
        )
        return json.loads(response.data)["token"]

    # ========== 400 BAD REQUEST TESTS ==========

    def test_400_missing_required_fields_customer_registration(self):
        """Test 400 when missing required fields in customer registration"""
        # Missing password
        response = self.client.post(
            "/customers/register", json={"email": "new@example.com"}
        )
        self.assertEqual(response.status_code, 400)

        # Missing email
        response = self.client.post(
            "/customers/register", json={"password": "password123"}
        )
        self.assertEqual(response.status_code, 400)

        # Empty JSON
        response = self.client.post("/customers/register", json={})
        self.assertEqual(response.status_code, 400)

    def test_400_missing_required_fields_mechanic_registration(self):
        """Test 400 when missing required fields in mechanic registration"""
        # Missing multiple fields
        response = self.client.post("/mechanics/register", json={"first_name": "John"})
        self.assertEqual(response.status_code, 400)

        # Missing password
        response = self.client.post(
            "/mechanics/register",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_400_missing_required_fields_service_ticket(self):
        """Test 400 when missing required fields in service ticket creation"""
        response = self.client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {self.customer_token}"},
            json={"description": "Test ticket"},
        )  # Missing customer_id
        self.assertEqual(response.status_code, 400)

    def test_400_missing_required_fields_inventory(self):
        """Test 400 when missing required fields in inventory creation"""
        # Missing price
        response = self.client.post("/inventory/", json={"name": "Test Part"})
        self.assertEqual(response.status_code, 400)

        # Missing name
        response = self.client.post("/inventory/", json={"price": 29.99})
        self.assertEqual(response.status_code, 400)

    def test_400_invalid_json_format(self):
        """Test 400 with invalid JSON format"""
        response = self.client.post(
            "/customers/login", data="invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_400_invalid_data_types_inventory(self):
        """Test 400 with invalid data types for inventory"""
        # Price as string instead of number
        response = self.client.post(
            "/inventory/", json={"part_name": "Test Part", "price": "invalid"}
        )  # Use   'part_name' not 'name'
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn(
            "Price must be a valid number", data["errors"]
        )  # Updated error message

        # Price as negative number
        response = self.client.post(
            "/inventory/", json={"part_name": "Test Part", "price": -10.00}
        )  # Use  'part_name' not 'name'
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Price cannot be negative", data["errors"])

        # Empty name - UPDATE THIS ASSERTION
        response = self.client.post(
            "/inventory/", json={"part_name": "", "price": 10.00}
        )  # Use 'part_name' not    'name'
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn(
            "part_name is required and cannot be empty", data["errors"]
        )  # Updated error message

    def test_400_invalid_data_types_other_endpoints(self):
        """Test 400 with invalid data types for other endpoints"""
        # Customer ID as string instead of integer
        response = self.client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {self.customer_token}"},
            json={"customer_id": "invalid", "description": "Test"},
        )
        self.assertEqual(response.status_code, 400)

    # ========== 401 UNAUTHORIZED TESTS ==========

    def test_401_missing_token_protected_endpoints(self):
        """Test 401 when accessing protected endpoints without token"""
        # Test endpoints that actually exist and require authentication
        endpoints = [
            # Customer endpoints requiring auth
            ("/customers/my-tickets", "GET"),  # Protected by @token_required
            # Service ticket endpoints requiring auth
            ("/tickets", "POST"),  # Protected by @token_required
            ("/tickets", "GET"),  # Protected by @token_required
            ("/tickets/1", "GET"),  # Protected by @token_required
            # Mechanic endpoints requiring auth
            ("/mechanics", "GET"),  # Protected by @mechanic_token_required
            ("/mechanics/1", "GET"),  # Protected by @mechanic_token_required
            ("/mechanics/1", "PUT"),  # Protected by @mechanic_token_required
            # Inventory endpoints requiring auth
            ("/inventory/1", "PUT"),  # Protected by @mechanic_token_required
            ("/inventory/1/archive", "PATCH"),  # Protected by @mechanic_token_required
            # REMOVED: ('/inventory/1', 'DELETE'),     # This endpoint doesn't exist
        ]

        for endpoint, method in endpoints:
            with self.subTest(endpoint=endpoint, method=method):
                if method == "GET":
                    response = self.client.get(endpoint)
                elif method == "POST":
                    response = self.client.post(endpoint, json={})
                elif method == "PUT":
                    response = self.client.put(endpoint, json={})
                elif method == "PATCH":
                    response = self.client.patch(endpoint, json={})
                elif method == "DELETE":
                    response = self.client.delete(endpoint)

                self.assertEqual(
                    response.status_code,
                    401,
                    f"Expected 401 for {method} {endpoint}, got {response.status_code}",
                )

                # Verify the error message
                if response.status_code == 401:
                    data = json.loads(response.data)
                    self.assertEqual(data["message"], "Token is missing")

    def test_401_invalid_token_format(self):
        """Test 401 with invalid token format"""
        headers = {"Authorization": "InvalidFormat"}
        response = self.client.get("/customers/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_401_expired_or_invalid_token(self):
        """Test 401 with expired or invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = self.client.get("/customers/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Token is invalid")

    def test_401_wrong_token_type_for_endpoint(self):
        """Test 403 when using wrong token type for endpoint"""
        # Using customer token for mechanic-only endpoint should return 403 (Forbidden)
        response = self.client.delete(
            f"/tickets/{self.ticket1.id}",
            headers={"Authorization": f"Bearer {self.customer_token}"},
        )

        # Should return 403 Forbidden (not 401 Unauthorized)
        self.assertEqual(response.status_code, 403)

        # Verify the error message
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Unauthorized - Mechanic token required")

    # ========== 404 NOT FOUND TESTS ==========

    def test_404_nonexistent_customer(self):
        """Test 404 when accessing nonexistent customer"""
        response = self.client.get("/customers/9999")
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/customers/9999", json={"email": "updated@example.com"}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete("/customers/9999")
        self.assertEqual(response.status_code, 404)

    def test_404_nonexistent_mechanic(self):
        """Test 404 when accessing nonexistent mechanic"""
        response = self.client.get(
            "/mechanics/9999",
            headers={"Authorization": f"Bearer {self.mechanic_token}"},
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.put(
            "/mechanics/9999",
            headers={"Authorization": f"Bearer {self.mechanic_token}"},
            json={"first_name": "Updated"},
        )
        self.assertEqual(response.status_code, 404)

    def test_404_nonexistent_service_ticket(self):
        """Test 404 when accessing nonexistent service ticket"""
        response = self.client.get(
            "/tickets/9999", headers={"Authorization": f"Bearer {self.customer_token}"}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(
            "/tickets/9999", headers={"Authorization": f"Bearer {self.mechanic_token}"}
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.put("/tickets/9999/edit", json={"add_ids": [1]})
        self.assertEqual(response.status_code, 404)

        response = self.client.post("/tickets/9999/add-part", json={"part_id": 1})
        self.assertEqual(response.status_code, 404)


def test_404_nonexistent_inventory(self):
    """Test 404 when accessing nonexistent inventory item"""
    # Get mechanic token for authenticated endpoints
    login_response = self.client.post(
        "/mechanics/login",
        json={"email": "mechanic1@example.com", "password": "mechanic123"},
    )
    token = json.loads(login_response.data)["token"]

    # Test 1: GET nonexistent inventory (no auth required)
    response = self.client.get("/inventory/999")
    self.assertEqual(response.status_code, 404, "GET /inventory/999 should return 404")

    # Test 2: PUT nonexistent inventory (requires auth)
    response = self.client.put(
        "/inventory/999",
        headers={"Authorization": f"Bearer {token}"},
        json={"part_name": "Updated Part", "price": 39.99},
    )
    self.assertEqual(response.status_code, 404, "PUT /inventory/999 should return 404")

    # Test 3: PATCH nonexistent inventory archive (requires auth)
    response = self.client.patch(
        "/inventory/999/archive", headers={"Authorization": f"Bearer {token}"}
    )
    self.assertEqual(
        response.status_code, 404, "PATCH /inventory/999/archive should return 404"
    )

    def test_404_nonexistent_part_in_ticket(self):
        """Test 404 when adding nonexistent part to ticket"""
        response = self.client.post(
            f"/tickets/{self.ticket1.id}/add-part", json={"part_id": 9999}
        )
        self.assertEqual(response.status_code, 404)

    def test_404_nonexistent_api_endpoint(self):
        """Test 404 for nonexistent API endpoint"""
        response = self.client.get("/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)

        response = self.client.post("/invalid/route", json={})
        self.assertEqual(response.status_code, 404)

    # ========== 409 CONFLICT TESTS ==========

    def test_409_duplicate_customer_email(self):
        """Test 409 when registering customer with duplicate email"""
        response = self.client.post(
            "/customers/register",
            json={"email": "customer1@example.com", "password": "password123"},
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn("already", data["message"].lower())

    def test_409_duplicate_mechanic_email(self):
        """Test 409 when registering mechanic with duplicate email"""
        response = self.client.post(
            "/mechanics/register",
            json={
                "first_name": "Duplicate",
                "last_name": "User",
                "email": "mechanic1@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn("already", data["message"].lower())

    def test_409_duplicate_inventory_name(self):
        """Test 409 when creating inventory with duplicate name"""
        response = self.client.post(
            "/inventory/", json={"name": "Brake Pads", "price": 59.99}
        )
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn("already exists", data["message"])

    # ========== BUSINESS LOGIC ERROR TESTS ==========

    def test_business_validation_errors_inventory(self):
        """Test various business logic validation errors for inventory"""
        # Negative price
        response = self.client.post(
            "/inventory/", json={"name": "Test Part", "price": -10.00}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Price cannot be negative", data["errors"])

        # Empty name
        response = self.client.post("/inventory/", json={"name": "", "price": 10.00})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Name is required and cannot be empty", data["errors"])

        # Very high price
        response = self.client.post(
            "/inventory/", json={"name": "Test Part", "price": 9999999.99}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Price seems unusually high", data["errors"])

    def test_invalid_pagination_parameters(self):
        """Test invalid pagination parameters"""
        response = self.client.get(
            "/customers/all?page=0&per_page=5"
        )  # page should be >= 1
        # This might return 400 or default to page 1

        response = self.client.get("/customers/all?page=-1&per_page=5")
        # This might return 400 or default to page 1

        response = self.client.get(
            "/customers/all?page=1&per_page=0"
        )  # per_page should be >= 1
        # This might return 400 or default to reasonable value

    def test_rate_limiting_errors(self):
        """Test rate limiting error responses"""
        # Make rapid requests to trigger rate limiting
        responses = []
        for i in range(20):  # More than the rate limit
            response = self.client.get("/customers/all")
            responses.append(response.status_code)

        # Should eventually get 429 Too Many Requests
        self.assertIn(429, responses)

    # ========== EDGE CASE TESTS ==========

    def test_empty_database_queries(self):
        """Test behavior when querying empty collections"""
        # Delete all inventory items
        Inventory.query.delete()
        db.session.commit()

        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])  # Should return empty array, not error

    def test_large_input_values(self):
        """Test handling of very large input values"""
        # Very large price (within reasonable limits)
        response = self.client.post(
            "/inventory/", json={"name": "Test", "price": 999999.99}
        )
        # This should succeed as it's within the validation limit

        # Very long description
        long_description = "x" * 1000
        response = self.client.post(
            "/tickets",
            headers={"Authorization": f"Bearer {self.customer_token}"},
            json={"customer_id": self.customer1.id, "description": long_description},
        )
        # This might succeed or return 400 based on validation

    def test_special_characters_in_input(self):
        """Test handling of special characters in input"""
        response = self.client.post(
            "/customers/register",
            json={"email": "test@example.com", "password": "password!@#$%"},
        )
        # Should handle special characters appropriately

    def test_malformed_ids_in_url(self):
        """Test handling of malformed IDs in URL parameters"""
        response = self.client.get("/customers/abc")  # Non-numeric ID
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/customers/1.5")  # Float ID
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/customers/-1")  # Negative ID
        self.assertEqual(response.status_code, 404)

    # ========== COMPREHENSIVE ENDPOINT COVERAGE ==========

    def test_all_endpoints_have_error_handling(self):
        """Verify all API endpoints have proper error handling"""
        endpoints_to_test = [
            # Customer endpoints
            ("/customers/login", "POST", 400),  # Missing credentials
            ("/customers/register", "POST", 400),  # Missing fields
            ("/customers/999", "GET", 404),  # Nonexistent customer
            ("/customers/999", "PUT", 404),  # Nonexistent customer
            ("/customers/999", "DELETE", 404),  # Nonexistent customer
            ("/customers/my-tickets", "GET", 401),  # No token
            # Mechanic endpoints
            ("/mechanics/login", "POST", 400),  # Missing credentials
            ("/mechanics/register", "POST", 400),  # Missing fields
            ("/mechanics/999", "GET", 404),  # Nonexistent mechanic
            ("/mechanics", "GET", 401),  # No token
            # Service ticket endpoints
            ("/tickets", "POST", 401),  # No token
            ("/tickets/999", "GET", 404),  # Nonexistent ticket
            ("/tickets/999", "DELETE", 404),  # Nonexistent ticket
            ("/tickets/999/edit", "PUT", 404),  # Nonexistent ticket
            ("/tickets/999/add-part", "POST", 404),  # Nonexistent ticket
            # Inventory endpoints
            ("/inventory/", "POST", 400),  # Missing fields
            ("/inventory/999", "PUT", 404),  # Nonexistent item
            ("/inventory/999", "DELETE", 404),  # Nonexistent item
            ("/inventory/999/archive", "PATCH", 404),  # Nonexistent item
        ]

        for endpoint, method, expected_status in endpoints_to_test:
            response = None  # ensure initialized for static analysis

            if method == "GET":
                response = self.client.get(endpoint)
            elif method == "POST":
                response = self.client.post(endpoint, json={})
            elif method == "PUT":
                response = self.client.put(endpoint, json={})
            elif method == "DELETE":
                response = self.client.delete(endpoint)
            elif method == "PATCH":
                response = self.client.patch(endpoint)

            # Explicitly assert response is not None for static/type analysis
            self.assertIsNotNone(
                response, f"Failed to create response object for {method} {endpoint}"
            )

            # Now safe to access response.status_code; keep extra guard for type checkers
            if response is None:
                # This should be unreachable, but keeps type checkers happy
                self.fail(f"Response is None for {method} {endpoint}")

            self.assertEqual(
                response.status_code,
                expected_status,
                f"Endpoint {method} {endpoint} should return {expected_status}",
            )
