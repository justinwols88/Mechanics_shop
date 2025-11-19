# In test_system.py
import unittest
import json
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from config import TestingConfig  # Import the actual config class


class SystemTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Pass the actual config class, not a string
        self.app = create_app(TestingConfig)  # Remove quotes - pass the class directly
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
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('database', data['services'])

    # In test_system.py, update the rate_limiting test:

def test_rate_limiting(self):
    """Test rate limiting on endpoints"""
    # Use an endpoint with lower rate limits for testing
    # Make rapid requests to trigger rate limiting
    responses = []
    for i in range(12):  # More than the rate limit of 10 per minute
        response = self.client.get('/customers/all')
        responses.append(response.status_code)
    
    # Should eventually get 429 Too Many Requests
    # Check if we got any 429 responses
    has_rate_limit = 429 in responses
    
    # If not, try a different approach - make requests faster
    if not has_rate_limit:
        responses = []
        # Make requests in quick succession
        for i in range(15):
            response = self.client.get('/customers/all')
            responses.append(response.status_code)
            # Small delay to ensure they're processed as separate requests
            import time
            time.sleep(0.01)
    
    self.assertIn(429, responses,
                 f"Expected 429 in responses, but got: {set(responses)}")

    def test_caching(self):
        """Test caching on cached endpoints"""
        # First request
        response1 = self.client.get('/inventory/')
        self.assertEqual(response1.status_code, 200)

        # Second request - should be served from cache
        response2 = self.client.get('/inventory/')
        self.assertEqual(response2.status_code, 200)

        # Both responses should be identical (cached)
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        self.assertEqual(data1, data2)

    def test_nonexistent_endpoint(self):
        """Test accessing a non-existent endpoint"""
        response = self.client.get('/nonexistent-endpoint')
        self.assertEqual(response.status_code, 404)

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token (negative test)"""
        response = self.client.get('/tickets/my-tickets')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Token is missing')

    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token (negative test)"""
        response = self.client.get('/tickets/my-tickets', 
                                 headers={'Authorization': 'Bearer invalidtoken123'})
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Token is invalid')

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get('/health')
        self.assertIn('Access-Control-Allow-Origin', response.headers)

    def test_json_content_type(self):
        """Test responses have correct content type"""
        response = self.client.get('/health')
        self.assertEqual(response.content_type, 'application/json')


if __name__ == '__main__':
    unittest.main()