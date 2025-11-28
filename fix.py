#!/usr/bin/env python3
"""
Run flake8 without configuration file issues
"""
import sys
import os
from flake8.main.application import Application

def main():
    # Remove any problematic environment variables
    os.environ.pop('FLAKE8_CONFIG', None)
    
    # Set up arguments for flake8
    args = [
        'app/', 
        'tests/',
        '--max-line-length=127',
        '--ignore=E302,E303,W293,W292,W291,E128,W391,F401,E305,E301,E402,F811,E122,E131,E501,W292',
        '--exclude=.git,__pycache__,build,dist,.venv,venv,migrations'
    ]
    
    # Run flake8 programmatically
    app = Application()
    app.run(args)
    
    # Exit with flake8's exit code
    sys.exit(app.exit_code())

if __name__ == '__main__':
    main()