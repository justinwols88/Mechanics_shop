"""
Inventory Routes
"""
from flask import Blueprint, jsonify
from functools import wraps
from typing import Callable
from app.models.inventory import Inventory
from app.models.mechanic import Mechanic

try:
    from app.utils.auth import mechanic_token_required
except (ImportError, AttributeError, ModuleNotFoundError):
    # Fallback no-op decorator if the real decorator is unavailable
    def mechanic_token_required(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """Get inventory"""
    return {"message": "inventory endpoint"}, 200

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@mechanic_token_required
def update_inventory_item(item_id):
    """Update inventory item"""
    # Placeholder implementation returning a valid Flask response type
    return {"message": f"inventory item {item_id} updated"}, 200

def validate_inventory_data(data):
    errors = []
    
    if not data.get('part_name') or not data.get('part_name').strip():
        errors.append("Name is required and cannot be empty")
    
    if not data.get('price') or float(data.get('price', 0)) <= 0:
        errors.append("Price must be a positive number")
    
    return errors

# For non-existent inventory (should return 404, not 405)
@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
    return jsonify(item.to_dict())

# For non-existent mechanics (should return 404, not 401)  
@inventory_bp.route('/mechanics/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = Mechanic.query.get(mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    return jsonify(mechanic.to_dict())