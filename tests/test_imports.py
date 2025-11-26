#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

def test_imports():
    """Test that all required imports work"""
    print("=== Testing Imports ===")
    
    # Add the parent directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    
    try:
        from app import create_app, db
        print('✓ SUCCESS: Imported create_app from app')
        
        from config import TestingConfig
        print('✓ SUCCESS: Imported TestingConfig from config')
        
        # Test app creation
        app = create_app(TestingConfig)
        print('✓ SUCCESS: App creation worked')
        
        # Test database operations WITHIN app context
        with app.app_context():
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