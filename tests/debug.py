import sys
import os
sys.path.insert(0, '.')

try:
    from app.extensions import ma
    print(f"ma type: {type(ma)}")
    print(f"ma value: {ma}")
    
    if hasattr(ma, 'SQLAlchemyAutoSchema'):
        print("✓ ma.SQLAlchemyAutoSchema exists")
    else:
        print("✗ ma.SQLAlchemyAutoSchema does not exist")
        
    # Test creating a simple schema
    from app.models import Customer
    
    class TestSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
            model = Customer
            load_instance = True
            
    print("✓ Schema creation successful")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()