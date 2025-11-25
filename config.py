"""
Configuration settings for Mechanics Shop API
"""

import os

class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///mechanics_shop.db"
    SECRET_KEY = "dev-secret-key"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///mechanics_shop.db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prod-super-secret-key')
    # For production, consider using Redis instead of SimpleCache
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SECRET_KEY = "test-secret-key"
