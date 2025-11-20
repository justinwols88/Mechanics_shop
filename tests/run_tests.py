#!/usr/bin/env python3
"""
Test runner for Mechanics Shop API
Run with: python run_tests.py
"""
import unittest
import sys
import os


def run_tests():
    """Run all tests and return results"""
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(__file__))

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    print("Running Mechanics Shop API Test Suite...")
    print("=" * 60)
    exit_code = run_tests()
    sys.exit(exit_code)
