from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate
import os

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# Initialize limiter with conditional enabling
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URI", "redis://localhost:6379"),
    default_limits=["100 per hour"],
    enabled=not os.getenv("TESTING"),  # Disable if TESTING environment variable is set
)

# Use Redis for caching
cache = Cache()
