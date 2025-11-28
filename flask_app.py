"""
Production entry point for Mechanics Shop API
"""
import os
from app import create_app
from config import ProductionConfig

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run()