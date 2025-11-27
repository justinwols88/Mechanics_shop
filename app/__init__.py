"""
Mechanics Shop API Application Factory
Initializes Flask app with all extensions and blueprints.
"""

import os
import sys
from datetime import datetime
from importlib.util import find_spec
from flask import Flask, jsonify
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError
from app.extensions import db, ma, cache, migrate, limiter

REQUIRED_PACKAGES = [
    "flask",
    "flask_sqlalchemy",
    "flask_marshmallow",
    "flask_caching",
    "flask_migrate",
    "flask_limiter",
    "flask_cors",
    "flask_swagger_ui",
]

def _verify_dependencies():
    missing = [p for p in REQUIRED_PACKAGES if find_spec(p) is None]
    if missing:
        raise ModuleNotFoundError(
            f"Missing packages: {', '.join(missing)}. "
            "Install with: pip install " + " ".join(REQUIRED_PACKAGES)
        )

_verify_dependencies()

from flask import Flask, jsonify
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError

# Import extensions
from app.extensions import db, ma, cache, migrate, limiter

# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"

def create_app(config_object=None):
    """
    Application factory function.
    Args:
        config_object: Configuration class to use
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Import here to avoid circular imports
    from config import ProductionConfig

    # Use provided config or default to ProductionConfig
    if config_object is None:
        config_object = ProductionConfig
    app.config.from_object(config_object)

    # Initialize extensions with app FIRST
    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    
    # Configure limiter
    from flask_limiter.util import get_remote_address
    limiter.init_app(app)
    
    from flask_cors import CORS
    CORS(app)

    # Import models to ensure they are registered with SQLAlchemy
    with app.app_context():
        from app import models  # This ensures models are loaded

    # Register blueprints with error handling
    try:
        # These imports are inside the function to avoid circular imports
        from app.blueprints.customers.routes import customers_bp
        from app.blueprints.service_tickets.routes import service_tickets_bp
        from app.blueprints.mechanics.routes import mechanics_bp
        from app.blueprints.inventory.routes import inventory_bp

        app.register_blueprint(customers_bp, url_prefix="/customers")
        app.register_blueprint(service_tickets_bp, url_prefix="/tickets")
        app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
        app.register_blueprint(inventory_bp, url_prefix="/inventory")

        print("✓ All blueprints registered successfully!")
    except ImportError as e:
        print(f"⚠️  Error importing blueprints: {e}")

    # Swagger UI
    try:
        from flask_swagger_ui import get_swaggerui_blueprint
        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL, API_URL, config={"app_name": "Mechanics Shop API"}
        )
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    except ImportError:
        print("⚠️  Flask-Swagger-UI not available")

    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Comprehensive health check for multiple services.
        Returns:
            JSON: Health status of all services with appropriate HTTP status code
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
        }

        try:
            # Check database
            db.session.execute(text("SELECT 1"))
            health_status["services"]["database"] = "healthy"
        except (OperationalError, ProgrammingError, SQLAlchemyError) as e:
            health_status["services"]["database"] = "unhealthy"
            health_status["status"] = "unhealthy"
            health_status["database_error"] = str(e)

        health_status["services"]["api"] = "healthy"

        status_code = 200 if health_status["status"] == "healthy" else 503

        return jsonify(health_status), status_code

    @app.route("/")
    def index():
        """
        Root endpoint with API information.
        Returns:
            JSON: API metadata and available endpoints
        """
        return jsonify(
            {
                "message": "Mechanics Shop API",
                "version": "1.0.0",
                "endpoints": {
                    "docs": "/docs",
                    "health": "/health",
                    "customers": "/customers",
                    "tickets": "/tickets",
                    "mechanics": "/mechanics",
                    "inventory": "/inventory",
                },
            }
        )

    return app