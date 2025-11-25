#!/usr/bin/env python3
"""
Script to fix CI/CD issues
"""

import os

def create_init_files():
    """Create necessary __init__.py files"""
    # Create tests/__init__.py
    tests_init = "tests/__init__.py"
    if not os.path.exists(tests_init):
        with open(tests_init, 'w') as f:
            f.write('')
        print("✓ Created tests/__init__.py")
    
    # Create app/__init__.py if it doesn't exist
    app_init = "app/__init__.py"
    if not os.path.exists(app_init):
        print("⚠️  app/__init__.py doesn't exist - this might be the problem!")

def check_structure():
    """Check project structure"""
    print("Project structure:")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # Show first 5 files
            if file.endswith('.py'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    create_init_files()
    check_structure()