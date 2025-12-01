"""
Application Factory Pattern for Mechanics Shop API
"""
from flask import Flask, jsonify
from sqlalchemy import text
from datetime import datetime, timezone
from config import Config
from app.extensions import db, ma, migrate, limiter, cache
from flask_swagger_ui import get_swaggerui_blueprint

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)  # Removed jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    # ========== SWAGGER UI CONFIGURATION ==========
    SWAGGER_URL = '/docs'  # URL for accessing Swagger UI
    API_URL = '/swagger.yaml'  # URL for your Swagger specification file
    
    # Create Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Mechanics Shop API",
            'layout': "BaseLayout",
            'deepLinking': True,
            'showExtensions': True,
            'showCommonExtensions': True
        }
    )
    
    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    # ========== END SWAGGER CONFIG ==========

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

    # ========== SERVE SWAGGER.YAML FILE ==========
    @app.route('/swagger.yaml')
    def serve_swagger():
        """Serve the Swagger YAML file"""
        try:
            with open('swagger.yaml', 'r') as file:
                content = file.read()
            return content, 200, {'Content-Type': 'text/yaml'}
        except FileNotFoundError:
            return jsonify({"error": "Swagger file not found"}), 404
    # Mark as accessed to satisfy static analyzers
    _ = serve_swagger
    
    @app.route('/')
    def index():
        """Redirect root to docs"""
        return '<h1>Mechanics Shop API</h1><p>Visit <a href="/docs">/docs</a> for API documentation</p>'
    # Mark as accessed to satisfy static analyzers
    _ = index
    # ========== END SWAGGER.YAML SERVING ==========

    # Fixed health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint with proper structure"""
        try:
            db.session.execute(text('SELECT 1'))
            database_status = 'healthy'
        except Exception:
            database_status = 'unhealthy'
            
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "database": database_status,
                "api": "healthy"
            }
        })

    # Mark as accessed to satisfy static analyzers
    _ = health_check

    return app