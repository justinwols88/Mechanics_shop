#!/usr/bin/env python3
"""
Script to automatically fix common Flake8 style issues
"""
import os
import re

def fix_file(filepath):
    """Fix common style issues in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Fix W292: Add newline at end of file
    if content and not content.endswith('\n'):
        content += '\n'

    # Fix W293: Remove whitespace from blank lines
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)

    # Fix W291: Remove trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    # Fix E128: Fix under-indented continuation lines
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith(('db.Column', 'onupdate=')) and len(line) > 1:
            # Add proper indentation for continuation lines
            if not line.startswith('    ' * 2):  # Should be at least 8 spaces
                fixed_lines.append('    ' * 2 + line.lstrip())
                continue
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fixed issues in {filepath}")
        return True
    return False

def main():
    """Main function to fix all files"""
    files_fixed = 0

    # Files that need manual fixes for F811 (redefinition)
    manual_fix_files = [
        'app/__init__.py',
        'app/blueprints/service_tickets/routes.py',
        'app/utils/auth.py'
    ]

    print("Fixing style issues...")

    # Walk through all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    files_fixed += 1

    print(f"\nFixed {files_fixed} files automatically.")
    print("\n⚠️  Manual fixes needed for these files:")
    for file in manual_fix_files:
        if os.path.exists(file):
            print(f"  - {file}")

    print("\nManual fixes required:")
    print("1. Remove duplicate imports (F811 errors)")
    print("2. Add 2 blank lines before function/class definitions (E302)")
    print("3. Remove extra blank lines (E303)")

if __name__ == '__main__':
    main()
