"""
Application Factory Pattern with Blueprint Structure
"""
from flask import Flask
from config import Config
from app.extensions import db, jwt, ma, migrate, limiter, cache

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    # Import and register blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.customers.routes import customers_bp
    from app.blueprints.mechanics.routes import mechanics_bp
    from app.blueprints.service_tickets.routes import service_tickets_bp
    from app.blueprints.inventory.routes import inventory_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            "status": "healthy",
            "timestamp": "2023-01-15T10:30:00Z",
            "services": {
                "database": "healthy",
                "api": "healthy"
            }
        }

    return app