"""
Inventory Routes - Fixed endpoints
"""
from flask import Blueprint, request, jsonify
from app.models.inventory import Inventory
from app.utils.auth import mechanic_token_required
from app import db

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """Get all inventory items - No auth required"""
    try:
        inventory_items = Inventory.query.all()
        return jsonify({
            "success": True,
            "data": {
                "inventory": [item.to_dict() for item in inventory_items],
                "count": len(inventory_items)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@inventory_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_inventory_item(current_mechanic_id):
    """Create a new inventory item - Mechanic auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['part_name', 'price']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Create inventory item
        inventory = Inventory(
            part_name=data['part_name'],
            part_number=data.get('part_number'),
            description=data.get('description'),
            quantity=data.get('quantity', 0),
            price=data['price'],
            category=data.get('category'),
            supplier=data.get('supplier'),
            min_stock_level=data.get('min_stock_level', 5)
        )

        db.session.add(inventory)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Inventory item created successfully",
            "data": inventory.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_inventory_item(item_id):
    """Get a specific inventory item by ID - No auth required"""
    try:
        item = db.session.get(Inventory, item_id)
        if not item:
            return jsonify({
                "success": False,
                "error": "Inventory item not found"
            }), 404

        return jsonify({
            "success": True,
            "data": item.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@mechanic_token_required
def update_inventory_item(current_mechanic_id, item_id):
    """Update an inventory item - Mechanic auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        item = db.session.get(Inventory, item_id)
        if not item:
            return jsonify({
                "success": False,
                "error": "Inventory item not found"
            }), 404

        data = request.get_json()

        # Update fields if provided
        updatable_fields = ['part_name', 'part_number', 'description', 'quantity', 
                           'price', 'category', 'supplier', 'min_stock_level']
        for field in updatable_fields:
            if field in data:
                setattr(item, field, data[field])

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Inventory item updated successfully",
            "data": item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@mechanic_token_required
def delete_inventory_item(current_mechanic_id, item_id):
    """Delete an inventory item - Mechanic auth required"""
    try:
        item = db.session.get(Inventory, item_id)
        if not item:
            return jsonify({
                "success": False,
                "error": "Inventory item not found"
            }), 404

        db.session.delete(item)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Inventory item deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@inventory_bp.route('/<int:item_id>/archive', methods=['PATCH'])
@mechanic_token_required
def archive_inventory_item(current_mechanic_id, item_id):
    """Archive an inventory item by setting quantity to 0 - Mechanic auth required"""
    try:
        item = db.session.get(Inventory, item_id)
        if not item:
            return jsonify({
                "success": False,
                "error": "Inventory item not found"
            }), 404

        item.quantity = 0
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Inventory item archived (quantity set to 0)",
            "data": item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500