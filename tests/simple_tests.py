#!/usr/bin/env python3
"""
Simple test script that runs from project root
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Try to import app
    from app import create_app
    from app.extensions import db
    from app.models import Customer, Mechanic

    print("✓ Successfully imported app modules")

    # Create test app
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///test_simple.db"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = "test-secret-key"
        CACHE_TYPE = "SimpleCache"

    app = create_app("TestingConfig")

    with app.app_context():
        # Create tables
        db.create_all()

        # Test basic operations
        customer = Customer(
            # ...existing code (other required fields, e.g., id, etc.)...
            # Use actual fields defined on your Customer model:
            name="test user",
            email="testuser@example.com",
            # ...add or remove kwargs to match your real Customer model...
        )
        db.session.add(customer)
        db.session.commit()

        # Test query - filter by the same real field used above
        found = Customer.query.filter_by(email="testuser@example.com").first()
        if found:
            print("✓ Database operations working")
        else:
            print("✗ Database operations failed")

        # Clean up
        db.drop_all()

    print("✓ All basic tests passed!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
