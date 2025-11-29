#!/usr/bin/env python3
"""
Robust test runner that handles missing environment variables
"""
import os
import subprocess
import sys

def setup_environment():
    """Set up test environment variables"""
    env_vars = {
        'FLASK_ENV': 'testing',
        'SECRET_KEY': 'test-secret-key-for-ci', 
        'DATABASE_URL': 'sqlite:///test.db'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"Set {key} = {value}")

def run_tests():
    """Run pytest with proper environment"""
    setup_environment()
    
    print("🚀 Running Tests with Environment:")
    for key in ['FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL']:
        print(f"  {key}: {os.environ.get(key, 'NOT SET')}")
    
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