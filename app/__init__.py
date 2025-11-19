from flask import Flask, jsonify
from .extensions import db, ma, cache, migrate, limiter
from app.blueprints.customers.routes import customers_bp
from app.blueprints.service_tickets.routes import service_tickets_bp
from app.blueprints.mechanics.routes import mechanics_bp
from app.blueprints.inventory.routes import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
from sqlalchemy import text
from flask_cors import CORS

# Swagger configuration
SWAGGER_URL = '/docs'
SWAGGER_UI_URL = '/static/swagger.yaml'
SWAGGER_CONFIG = {
    'title': 'Service API Documentation',
    'version': '1.0',
    'openapi': '3.0.0',
    'x-logo-url': 'https://example.com/logo.png'
}

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    SWAGGER_UI_URL,
    config=SWAGGER_CONFIG
)

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Cache configuration
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 60

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Configure limiter based on app config
    if app.config.get('TESTING'):
        limiter.enabled = False
    
    limiter.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(service_tickets_bp, url_prefix='/tickets')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/health', methods=['GET'])
    def health_check():
        """Comprehensive health check for multiple services"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {}
        }
        
        try:
            # Check database
            db.session.execute(text('SELECT 1'))
            health_status['services']['database'] = 'healthy'
        except Exception as e:
            health_status['services']['database'] = 'unhealthy'
            health_status['status'] = 'unhealthy'
            health_status['database_error'] = str(e)
        
        health_status['services']['api'] = 'healthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify(health_status), status_code

    return app