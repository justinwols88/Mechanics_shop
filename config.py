import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:password@localhost/mechanics_shop"

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SWAGGER_HOST = os.environ.get('SWAGGER_HOST', 'https://mechanics-shop-revised-refactored-final.onrender.com')
    SWAGGER_SCHEMES = ['https']