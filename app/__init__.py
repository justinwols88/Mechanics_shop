"""
Flask Application Factory
"""
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
from config import Config
from flask import Flask
from .extensions import db, migrate, cache

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
cors = CORS()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    cors.init_app(app)


    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app

def register_blueprints(app):
    """Register all blueprints with the application"""
    try:
        from app.blueprints.customers.routes import customers_bp
        from app.blueprints.mechanics.routes import mechanics_bp
        from app.blueprints.inventory.routes import inventory_bp
        from app.blueprints.service_tickets.routes import service_tickets_bp
        from app.blueprints.auth.routes import auth_bp

        app.register_blueprint(customers_bp, url_prefix='/customers')
        print("✓ Customers blueprint registered successfully!")
        app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
        print("✓ Mechanics blueprint registered successfully!")
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        print("✓ Inventory blueprint registered successfully!")
        app.register_blueprint(service_tickets_bp, url_prefix='/tickets')
        print("✓ Service Tickets blueprint registered successfully!")
        app.register_blueprint(auth_bp, url_prefix='/auth')
        print("✓ All blueprints registered successfully!")
    

        # Health check endpoint
        @app.route('/health')
        def health_check():
            return jsonify({
                "status": "healthy",
                "message": "Mechanics Shop API is running",
                "timestamp": "2024-01-01T00:00:00Z"
            })

        print("✓ All blueprints registered successfully!")
        
    except ImportError as e:
        print(f"⚠️  Error importing blueprints: {e}")
    except Exception as e:
        print(f"⚠️  Error registering blueprints: {e}")

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request"}), 400
