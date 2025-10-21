from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanic_shop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    db.init_app(app)
    ma.init_app(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app import models
    
    # Import and register blueprints
    from app.customer.routes import customer_bp
    from app.mechanic.routes import mechanic_bp
    from app.service_ticket.routes import service_ticket_bp
    
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(mechanic_bp, url_prefix='/mechanics')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-tickets')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
