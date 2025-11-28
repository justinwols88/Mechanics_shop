#!/usr/bin/env python3
"""Add missing newlines to Python files"""
import os

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content and not content.endswith('\n'):
                    with open(filepath, 'a', encoding='utf-8') as f:
                        f.write('\n')
                    print(f"Added newline to {filepath}")
            except Exception as e:
                print(f"Error with {filepath}: {e}")
