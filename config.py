import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis for rate limiting and caching
    CACHE_TYPE = 'RedisCache'
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
    # Use env var if set, otherwise fall back to default sqlite db
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    CACHE_TYPE = "SimpleCache"
