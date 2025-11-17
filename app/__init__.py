from flask import Flask, jsonify
from flask_caching import Cache
from flask_limiter import Limiter
from .extensions import db, ma, cache, migrate
from flask_limiter.util import get_remote_address
from app.blueprints.customers.routes import customers_bp
from app.blueprints.service_tickets.routes import service_tickets_bp
from app.blueprints.mechanics.routes import mechanics_bp
from app.blueprints.inventory.routes import inventory_bp
from datetime import datetime
from sqlalchemy import text

limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(service_tickets_bp, url_prefix='/tickets')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

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
        
        # You can add more service checks here
        health_status['services']['api'] = 'healthy'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify(health_status), status_code

    return app