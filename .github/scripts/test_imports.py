#!/usr/bin/env python3
"""
Test script for GitHub Actions - Tests all imports and basic functionality
"""

import sys
import os
def main():
    print("=== Testing Imports ===")
    
    # Add current directory to Python path
    current_dir = os.getcwd()
    sys.path.insert(0, current_dir)
    print(f"Working directory: {current_dir}")
    print(f"Python path: {sys.path}")
    
    try:
        # Test basic imports
        from app import create_app, db
        print('✓ SUCCESS: Imported create_app from app')
        
        from config import TestingConfig
        print('✓ SUCCESS: Imported TestingConfig from config')
        
        # Test app creation
        app = create_app(TestingConfig)
        print('✓ SUCCESS: App creation worked')
        
        # Test database operations within app context
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
    success = main()
    sys.exit(0 if success else 1)