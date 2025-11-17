from flask import Blueprint, request, jsonify
from app.models import Inventory, Mechanic
from app.extensions import db
from app.schemas import InventorySchema
from app.utils.auth import mechanic_token_required
from app.extensions import limiter
from datetime import datetime, timedelta

inventory_bp = Blueprint('inventory', __name__)
inventory_schema = InventorySchema()

@inventory_bp.route('/', methods=['POST'])
def create_inventory():
    data = request.get_json()

    # Validate required fields
    if not data.get('name') or not data.get('price'):
        return {"message": "Name and price are required"}, 400

    # Create inventory part
    part = Inventory()
    part.name = data['name']
    part.price = data['price']
    db.session.add(part)
    db.session.commit()

    return inventory_schema.dump(part), 201
@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    parts = Inventory.query.all()
    return inventory_schema.dump(parts, many=True)


@inventory_bp.route('/<int:item_id>', methods=['PUT', 'PATCH'])
@mechanic_token_required
@limiter.limit("20 per minute")  # Reasonable limit for update operations
def update_inventory_item(current_mechanic_id, item_id):
    """Update inventory item with auth, rate limiting, and enhanced validation"""
    try:
        item = Inventory.query.get(item_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': f'Inventory item with id {item_id} not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided for update'
            }), 400
        
        # Validate input data
        errors = inventory_schema.validate(data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': errors
            }), 400
        
        # Enhanced business logic validations
        validation_errors = []
        
        if 'price' in data:
            if data['price'] < 0:
                validation_errors.append('Price cannot be negative')
            elif data['price'] > 10000:  # Reasonable upper limit
                validation_errors.append('Price seems unusually high')
        
        if 'quantity_in_stock' in data:
            if data['quantity_in_stock'] < 0:
                validation_errors.append('Quantity cannot be negative')
            elif data['quantity_in_stock'] > 1000:  # Reasonable upper limit
                validation_errors.append('Quantity seems unusually high')
        
        if 'name' in data and len(data['name'].strip()) == 0:
            validation_errors.append('Name cannot be empty')
        
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Business validation failed',
                'details': validation_errors
            }), 400
        
        # Track changes for audit (optional)
        changes = {}
        for key, value in data.items():
            if hasattr(item, key) and getattr(item, key) != value:
                changes[key] = {
                    'old': getattr(item, key),
                    'new': value
                }
                setattr(item, key, value)
        
        db.session.commit()
        
        result = inventory_schema.dump(item)
        response_data = {
            'success': True,
            'message': 'Inventory item updated successfully',
            'data': result
        }
        
        # Include changes in response for debugging (optional)
        if changes:
            response_data['changes'] = changes
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventory_bp.route('/<int:item_id>/archive', methods=['PATCH'])
@mechanic_token_required
def archive_inventory_item(current_mechanic_id, item_id):
    """Archive inventory item by setting quantity to 0"""
    try:
        item = Inventory.query.get(item_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': f'Inventory item with id {item_id} not found'
            }), 404
        
        # Set quantity to 0
        item.quantity_in_stock = 0
        item.updated_at = datetime.utcnow()
        
        # Optional: Set status
        if hasattr(item, 'status'):
            item.status = 'out_of_stock'
        
        db.session.commit()
        
        result = inventory_schema.dump(item)
        return jsonify({
            'success': True,
            'message': f'Inventory item archived (quantity set to 0)',
            'data': result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500