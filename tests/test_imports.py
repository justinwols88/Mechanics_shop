#!/usr/bin/env python3
"""Test all imports work correctly"""
import sys
import os

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")
print(f"Parent directory: {parent_dir}")

try:
    from app import create_app
    print("✓ Main app import successful")
    
    from app.blueprints.auth.routes import auth_bp
    print("✓ Auth blueprint import successful")
    
    from app.blueprints.customers.routes import customers_bp
    print("✓ Customers blueprint import successful")
    
    from app.blueprints.mechanics.routes import mechanics_bp
    print("✓ Mechanics blueprint import successful")
    
    from app.blueprints.inventory.routes import inventory_bp
    print("✓ Inventory blueprint import successful")
    
    from app.blueprints.service_tickets.routes import service_tickets_bp
    print("✓ Service tickets blueprint import successful")
    
    # Test creating the app
    app = create_app()
    print("✓ App creation successful")
    
    print("✓ All imports and app creation successful!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()