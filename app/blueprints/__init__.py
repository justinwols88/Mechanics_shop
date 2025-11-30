"""
Blueprints package - organized by module
"""
# Import blueprints to make them available
from app.blueprints.auth.routes import auth_bp
from app.blueprints.customers.routes import customers_bp
from app.blueprints.mechanics.routes import mechanics_bp
from app.blueprints.service_tickets.routes import service_tickets_bp
from app.blueprints.inventory.routes import inventory_bp

__all__ = ['auth_bp', 'customers_bp', 'mechanics_bp', 'service_tickets_bp', 'inventory_bp']