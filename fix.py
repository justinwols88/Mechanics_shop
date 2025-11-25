#!/usr/bin/env python3
"""
Quick script to fix the most critical flake8 issues
"""

import os
import re

def add_final_newline(filepath):
    """Ensure files end with a newline"""
    with open(filepath, 'r+', encoding='utf-8') as f:
        content = f.read()
        if content and not content.endswith('\n'):
            f.write('\n')

def remove_unused_imports(filepath):
    """Remove specific unused imports"""
    unused_patterns = [
        'from app.models import Mechanic',
        'from app.models import ServiceTicket', 
        'import numbers',
        'from sqlalchemy import func',
        'from urllib import response',
        'from flask import config',
        'from config import TestingConfig',
        'import json'
    ]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip lines that contain unused imports
        if any(pattern in line for pattern in unused_patterns):
            continue
        new_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

def fix_auth_imports(filepath):
    """Fix the JWTError import issue"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the duplicate import
    content = content.replace(
        'from jose.exceptions import JWTError', 
        '# JWTError imported below'
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_indentation(filepath):
    """Fix specific indentation issues"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific indentation issue at line 88
    lines = content.split('\n')
    if len(lines) > 87:
        # Fix line 88 (index 87) - ensure proper 4-space indentation
        lines[87] = '        print("✓ All blueprints registered successfully!")'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def remove_whitespace_lines(filepath):
    """Remove blank lines that contain whitespace"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove lines that are only whitespace
    lines = content.split('\n')
    new_lines = [line for line in lines if line.strip() != '' or line == '']
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

def fix_config_spacing(filepath):
    """Fix spacing in config.py"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure proper spacing between class definitions
    content = content.replace('class Config', '\n\nclass Config')
    content = content.replace('class DevelopmentConfig', '\n\nclass DevelopmentConfig')
    content = content.replace('class ProductionConfig', '\n\nclass ProductionConfig')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Apply fixes to specific files
files_to_fix = [
    './__init__.py',
    './app/__init__.py', 
    './app/blueprints/inventory/routes.py',
    './app/blueprints/mechanics/routes.py',
    './app/utils/auth.py',
    './config.py',
    './flask_app.py',
    './tests/run_comprehensive_tests.py',
    './tests/simple_tests.py'
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        print(f"Fixing {filepath}")
        
        if 'auth.py' in filepath:
            fix_auth_imports(filepath)
        elif 'config.py' in filepath:
            fix_config_spacing(filepath)
        elif filepath.endswith('__init__.py'):
            remove_whitespace_lines(filepath)
            fix_indentation(filepath)
        else:
            remove_unused_imports(filepath)
        
        add_final_newline(filepath)

print("✓ Quick fixes applied!")