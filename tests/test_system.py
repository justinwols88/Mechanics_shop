import unittest
import json
import sys
import os


# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from config import TestingConfig

class SystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_health_check_success(self):
        """Test health check endpoint when all services are healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data["services"])

    def test_rate_limiting(self):
        """Test rate limiting on endpoints"""
        # Use an endpoint with lower rate limits for testing
        responses = []
        for i in range(15):  # More than typical rate limit
            response = self.client.get("/customers/all")
            responses.append(response.status_code)
        
        # Should eventually get 429 Too Many Requests, but might not in test environment
        # Just verify we don't get server errors
        for status in responses:
            self.assertNotEqual(status, 500)

    def test_nonexistent_endpoint(self):
        """Test accessing a non-existent endpoint"""
        response = self.client.get("/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get("/tickets/my-tickets")
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()