"""
Inventory Routes
"""
from flask import Blueprint

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """Get inventory"""
    return {"message": "inventory endpoint"}, 200
