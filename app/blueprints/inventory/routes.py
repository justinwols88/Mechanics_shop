from flask import Blueprint, request, jsonify
from app.models import Inventory, Mechanic
from app.extensions import db
from app.schemas import InventorySchema
from app.utils.auth import mechanic_token_required
from app.extensions import limiter
from datetime import datetime, timezone
import numbers

inventory_bp = Blueprint('inventory_bp', __name__)
inventory_schema = InventorySchema()

def validate_inventory_data(data):
    """Validate inventory input data"""
    errors = []
    
    # Check required fields - use 'part_name' not 'name'
    if 'part_name' not in data or not data['part_name'] or not data['part_name'].strip():
        errors.append("part_name is required and cannot be empty")
    
    if 'price' not in data:
        errors.append("Price is required")
    else:
        # Validate price is a number and positive
        try:
            price = float(data['price'])
            if price < 0:
                errors.append("Price cannot be negative")
            elif price > 1000000:  # Reasonable upper limit
                errors.append("Price seems unusually high")
        except (ValueError, TypeError):
            errors.append("Price must be a valid number")
    
    # Validate name length
    if 'part_name' in data and len(data['part_name'].strip()) > 255:
        errors.append("part_name is too long (max 255 characters)")
    
    return errors

@inventory_bp.route('/', methods=['POST'])
def create_inventory():
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"message": "No data provided"}), 400

    # Validate input data
    validation_errors = validate_inventory_data(data)
    if validation_errors:
        return jsonify({
            "message": "Validation failed",
            "errors": validation_errors
        }), 400

    # Check if inventory item already exists - USE part_name NOT name
    existing_item = db.session.query(Inventory).filter_by(part_name=data['part_name'].strip()).first()
    if existing_item:
        return jsonify({"message": "Inventory item with this name already exists"}), 409

    # Create inventory part
    try:
        part = Inventory()
        part.part_name = data['part_name'].strip()
        part.price = float(data['price'])  # Convert to float after validation
        db.session.add(part)
        db.session.commit()

        return inventory_schema.dump(part), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error creating inventory item",
            "error": str(e)
        }), 500

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    parts = Inventory.query.all()
    return inventory_schema.dump(parts, many=True)


@inventory_bp.route('/<int:item_id>', methods=['PUT', 'PATCH'])
@mechanic_token_required
@limiter.limit("20 per minute")
def update_inventory_item(current_mechanic_id, item_id):
    """Update inventory item with auth, rate limiting, and enhanced validation"""
    try:
        item = db.session.get(Inventory, item_id)
        
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
        validation_errors = []
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    validation_errors.append('Price cannot be negative')
                elif price > 1000000:
                    validation_errors.append('Price seems unusually high')
            except (ValueError, TypeError):
                validation_errors.append('Price must be a valid number')
        
        if 'name' in data:
            name = data['part_name'].strip()
            if not name:
                validation_errors.append('Name cannot be empty')
            elif len(name) > 255:
                validation_errors.append('Name is too long (max 255 characters)')
            else:
                # Check for duplicate name (excluding current item)
                existing = Inventory.query.filter(
                    Inventory.part_name == name,
                    Inventory.id != item_id
                ).first()
                if existing:
                    validation_errors.append('Inventory item with this name already exists')
        
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Track changes for audit (optional)
        changes = {}
        for key, value in data.items():
            if hasattr(item, key):
                if key == 'price':
                    # Convert price to float
                    try:
                        value = float(value)
                    except (ValueError, TypeError):
                        return jsonify({
                            'success': False,
                            'error': f'Invalid value for {key}: must be a number'
                        }), 400
                
                if key == 'name':
                    value = value.strip()
                
                if getattr(item, key) != value:
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
        item = db.session.get(Inventory, item_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': f'Inventory item with id {item_id} not found'
            }), 404
        
        # Set quantity to 0 (if quantity field exists)
        if hasattr(item, 'quantity_in_stock'):
            item.quantity_in_stock = 0
        item.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        result = inventory_schema.dump(item)
        return jsonify({
            'success': True,
            'message': f'Inventory item archived',
            'data': result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500