import os
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()

# Fix for SQLAlchemyAutoSchema import without assigning to Marshmallow instance
try:
    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
except ImportError:
    SQLAlchemyAutoSchema = None
    print("Warning: marshmallow_sqlalchemy not installed")

# Initialize limiter with MEMORY storage for testing
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # Use memory instead of Redis
    default_limits=["200 per day", "50 per hour"],
    strategy="fixed-window",  # Avoid moving-window strategy issues
    enabled=not os.getenv("TESTING"),  # Disable if TESTING environment variable is set
)

# Use SimpleCache for testing
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# Explicitly define public exports and include SQLAlchemyAutoSchema if available
__all__ = ['db', 'ma', 'migrate', 'limiter', 'cache']
if SQLAlchemyAutoSchema is not None:
    __all__.append('SQLAlchemyAutoSchema')