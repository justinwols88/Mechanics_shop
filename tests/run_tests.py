#!/usr/bin/env python3
"""
Run tests and provide a summary
"""
import subprocess
import sys

def run_tests():
    """Run pytest and return results"""
    print("🚀 Running Mechanics Shop API Tests...")
    print("=" * 50)
    
    try:
        # Run pytest with verbose output
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
        
        print("=" * 50)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        elif result.returncode == 5:
            print("⚠️  No tests were collected")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)