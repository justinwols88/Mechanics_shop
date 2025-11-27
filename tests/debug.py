import sys
import os
sys.path.insert(0, '.')

print("=== Testing Circular Import Fix ===")

try:
    # Test importing models
    from app.models import Customer, ServiceTicket, Mechanic, Inventory
    print("✓ All models imported successfully!")
    
    # Test creating instances
    customer = Customer()
    customer.email = "test@example.com"
    customer.password = "password"
    print("✓ Customer instance created!")
    
    # Test Marshmallow schemas
    from app.extensions import ma
    print(f"✓ Marshmallow SQLAlchemyAutoSchema: {ma.SQLAlchemyAutoSchema}")
    
    from app.schemas import CustomerSchema
    print("✓ CustomerSchema imported successfully!")
    
    schema = CustomerSchema()
    print("✓ Schema instance created!")
    
    print("🎉 ALL TESTS PASSED!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()