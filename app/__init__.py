from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

db = SQLAlchemy()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanic_shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Rate limiting configuration
    app.config['RATELIMIT_STORAGE_URL'] = 'memory://'
    
    # Caching configuration - using simple in-memory cache for development
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes
    
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app import models
    
    # Import and register blueprints
    from app.mechanic.routes import mechanic_bp
    from app.service_ticket.routes import service_ticket_bp
    
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
