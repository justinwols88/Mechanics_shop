#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

def test_imports():
    """Test that all required imports work"""
    print("=== Testing Imports ===")
    
    try:
        from app import create_app
        print('✓ SUCCESS: Imported create_app from app')
        
        from config import TestingConfig
        print('✓ SUCCESS: Imported TestingConfig from config')
        
        # Test app creation
        app = create_app(TestingConfig)
        print('✓ SUCCESS: App creation worked')
        
        # Test database operations
        with app.app_context():
            from app.extensions import db
            db.create_all()
            print('✓ SUCCESS: Database operations worked')
            db.drop_all()
            
        print("✓ ALL IMPORTS SUCCESSFUL!")
        return True
        
    except Exception as e:
        print('✗ FAILED:', e)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)