import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis for rate limiting and caching
    CACHE_TYPE = 'SimpleCache'
    CACHE_REDIS_URL = os.getenv('REDIS_URI', 'redis://localhost:6379')

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'  # Use simple cache for testing
    TESTING = True

    # More aggressive rate limits for testing
    RATELIMIT_DEFAULT = "5 per minute"
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_ENABLED = False

class ProductionConfig(Config):
    # Use env var if set, otherwise fall back to default postgres or sqlite db
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    CACHE_TYPE = "SimpleCache"
