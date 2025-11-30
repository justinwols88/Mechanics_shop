#!/usr/bin/env python3
"""
Simple test runner that ensures database is set up
"""
import os
import subprocess
import sys

def setup_test_environment():
    """Set up test environment variables"""
    env_vars = {
        'FLASK_ENV': 'testing',
        'SECRET_KEY': 'test-secret-key-for-ci', 
        'DATABASE_URL': 'sqlite:///test.db'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key} = {value}")

def create_test_database():
    """Create test database tables"""
    try:
        from app import create_app, db
        from config import TestingConfig
        
        app = create_app(TestingConfig)
        with app.app_context():
            db.create_all()
            print("✅ Test database tables created")
    except Exception as e:
        print(f"❌ Error creating test database: {e}")

def run_tests():
    """Run pytest with proper environment"""
    setup_test_environment()
    create_test_database()
    
    print("🚀 Running Tests with Environment:")
    for key in ['FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL']:
        print(f"  {key}: {os.environ.get(key)}")
    
    print("\n" + "="*50)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v',
            '--tb=short',
            '--disable-warnings'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print("="*50)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)