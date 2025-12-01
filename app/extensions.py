import os
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# Junction tables for many-to-many relationships
service_mechanic = db.Table('service_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id')),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'))
)

ticket_inventory = db.Table('ticket_inventory',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id')),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'))
)

# Initialize limiter with MEMORY storage for testing
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day", "50 per hour"],
    strategy="fixed-window",
    enabled=not os.getenv("TESTING"),
)

# Use SimpleCache for testing
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

__all__ = ['db', 'ma', 'migrate', 'limiter', 'cache', 'service_mechanic', 'ticket_inventory']