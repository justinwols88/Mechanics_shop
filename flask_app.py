"""
Production entry point for Mechanics Shop API - UPDATED FOR PRODUCTION
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Only load .env in development, not production
if os.environ.get('FLASK_ENV') == 'development':
    from dotenv import load_dotenv
    load_dotenv()

from app import create_app
from config import ProductionConfig

# Use ProductionConfig for deployment
app = create_app(ProductionConfig)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)