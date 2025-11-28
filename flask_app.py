"""
Production entry point for Mechanics Shop API
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)