import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TestingConfig

class MinimalTestCase(unittest.TestCase):
    """Minimal test to verify basic functionality"""
    
    def setUp(self):
        from app import create_app
        from app.extensions import db
        
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
    
    def tearDown(self):
        from app.extensions import db
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_health_endpoint(self):
        """Test health endpoint works"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
    
    def test_customer_creation(self):
        """Test basic customer creation"""
        from app.models import Customer
        
        # Create customer and set fields directly (constructor may not accept keyword args)
        customer = Customer()
        customer.email = "test@example.com"
        customer.password = "password123"
        
        from app.extensions import db
        db.session.add(customer)
        db.session.commit()
        
        # Verify customer was created
        found_customer = Customer.query.filter_by(email="test@example.com").first()
        self.assertIsNotNone(found_customer, "Customer was not created or could not be found by email")
        if not found_customer:
            return
        self.assertEqual(found_customer.email, "test@example.com")

if __name__ == "__main__":
    unittest.main()