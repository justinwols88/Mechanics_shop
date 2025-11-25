"""
Mechanics Shop API Application Factory
Initializes Flask app with all extensions and blueprints.
"""

# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_caching import Cache
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError

# Add the parent directory to Python path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()
cache = Cache()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Swagger configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Mechanics Shop API"}
)


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

    # Configure limiter storage (add this after initialization)
    # For production, you should use Redis, but for now we'll use memory with a warning suppression
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    # Re-initialize limiter with storage configuration
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",  # Explicitly set to memory
        strategy="fixed-window"   # Add strategy to reduce warnings
    )

    # Initialize extensions with app
    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    CORS(app)

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
        print(f"✗ Error importing blueprints: {e}")

    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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
