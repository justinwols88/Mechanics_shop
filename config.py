import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-production-secret-key')
    
    # Handle database URL with proper fallbacks
    database_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
    
    if database_url:
        # Fix PostgreSQL URL format
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'SimpleCache'

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    TESTING = True
    RATELIMIT_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False