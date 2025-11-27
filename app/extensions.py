from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# Make sure SQLAlchemyAutoSchema is available
try:
    # Force import to ensure SQLAlchemyAutoSchema is available
    from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
    # Add it to ma if it's missing
    if not hasattr(ma, 'SQLAlchemyAutoSchema'):
        ma.SQLAlchemyAutoSchema = SQLAlchemyAutoSchema
except ImportError:
    print("Warning: marshmallow_sqlalchemy not installed")

# Initialize limiter with conditional enabling
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URI", "redis://localhost:6379"),
    default_limits=["100 per hour"],
    enabled=not os.getenv("TESTING"),
)

# Use Redis for caching
cache = Cache()