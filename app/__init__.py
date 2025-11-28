"""
Flask Application Factory
"""
import os
import sys
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
from config import ProductionConfig

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
cors = CORS()

def create_app(config_class=ProductionConfig):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load appropriate config
    if os.environ.get('FLASK_ENV') == 'development':
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

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
        # Use absolute imports
        from app.blueprints.auth.routes import auth_bp
        from app.blueprints.customers.routes import customers_bp
        from app.blueprints.mechanics.routes import mechanics_bp
        from app.blueprints.inventory.routes import inventory_bp
        from app.blueprints.service_tickets.routes import service_tickets_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(customers_bp, url_prefix='/customers')
        app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
        app.register_blueprint(inventory_bp, url_prefix='/inventory')
        app.register_blueprint(service_tickets_bp, url_prefix='/tickets')

        # Health check endpoint
        @app.route('/health')
        def health_check():
            return jsonify({
                "status": "healthy",
                "message": "Mechanics Shop API is running",
                "environment": os.environ.get('FLASK_ENV', 'production')
            })

        print("✓ All blueprints registered successfully!")
        
    except ImportError as e:
        print(f"⚠️  Error importing blueprints: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"⚠️  Error registering blueprints: {e}")
        import traceback
        traceback.print_exc()

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