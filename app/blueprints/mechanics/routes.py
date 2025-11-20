from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.models import Mechanic, ServiceTicket
from app.extensions import db
from app.utils.auth import encode_mechanic_token, mechanic_token_required
from app.schemas import MechanicSchema, MechanicsSchema
from app.extensions import limiter, cache

mechanics_bp = Blueprint('mechanics_bp', __name__)
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicsSchema()

@mechanics_bp.route('/ranking', methods=['GET'])
def mechanics_ranking():
    """Get mechanics ordered by ticket count - generic safe version"""
    try:
        # Get all mechanics
        mechanics = Mechanic.query.all()
        
        # Create a list with ticket counts
        mechanics_data = []
        for mechanic in mechanics:
            # Safely get attributes with fallbacks
            ticket_count = len(mechanic.tickets) if hasattr(mechanic, 'tickets') and mechanic.tickets else 0
            
            # Build mechanic data safely
            mechanic_info = {
                "id": mechanic.id,
                "ticket_count": ticket_count
            }
            
            # Add name field if it exists (try common variations)
            if hasattr(mechanic, 'name'):
                mechanic_info["name"] = mechanic.name
            elif hasattr(mechanic, 'first_name') and hasattr(mechanic, 'last_name'):
                mechanic_info["name"] = f"{mechanic.first_name} {mechanic.last_name}"
            elif hasattr(mechanic, 'first_name'):
                mechanic_info["name"] = mechanic.first_name
            else:
                mechanic_info["name"] = f"Mechanic {mechanic.id}"
            
            # Add email if it exists
            if hasattr(mechanic, 'email'):
                mechanic_info["email"] = mechanic.email
            
            # Add other fields that might exist
            if hasattr(mechanic, 'specialty'):
                mechanic_info["specialty"] = mechanic.specialty
            elif hasattr(mechanic, 'specialization'):
                mechanic_info["specialty"] = mechanic.specialization
            elif hasattr(mechanic, 'skill'):
                mechanic_info["specialty"] = mechanic.skill
            
            mechanics_data.append(mechanic_info)
        
        # Sort by ticket count descending
        mechanics_data.sort(key=lambda x: x['ticket_count'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': mechanics_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mechanics_bp.route('/login', methods=['POST'])
def mechanic_login():
    data = request.get_json()

    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    # Check mechanic credentials
    mechanic = Mechanic.query.filter_by(email=data['email']).first()
    if not mechanic or mechanic.password != data['password']:
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate JWT token
    token = encode_mechanic_token(mechanic.id)
    return jsonify({"token": token}), 200


@mechanics_bp.route('/register', methods=['POST'])
def register_mechanic():
    data = request.get_json()

    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    # Check if mechanic already exists by email
    if Mechanic.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409

    # Create new mechanic
    new_mechanic = Mechanic(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=data['password']
    )
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.dump(new_mechanic), 201


@mechanics_bp.route('', methods=['GET'])
@mechanic_token_required
def get_mechanics(current_mechanic):
    """Get all mechanics (requires mechanic authentication)"""
    try:
        mechanics = Mechanic.query.all()
        result = mechanics_schema.dump(mechanics)
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@mechanic_token_required
@cache.cached(timeout=30)
@limiter.limit("20 per minute")
def get_mechanic(current_user, mechanic_id):
    """Get specific mechanic with auth, caching, and rate limiting"""
    try:
        mechanic = Mechanic.query.get(mechanic_id)
        
        if not mechanic:
            return jsonify({
                'success': False,
                'error': f'Mechanic with id {mechanic_id} not found'
            }), 404
        
        result = mechanic_schema.dump(mechanic)
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT', 'PATCH'])
@mechanic_token_required
def update_mechanic(current_mechanic_id, mechanic_id):
    """Update mechanic - expecting ID from decorator"""
    try:
        mechanic = Mechanic.query.get(mechanic_id)
        
        if not mechanic:
            return jsonify({
                'success': False,
                'error': f'Mechanic with id {mechanic_id} not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided for update'
            }), 400
        
        # Validate input data
        errors = mechanic_schema.validate(data, partial=True)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': errors
            }), 400
        
        # Update mechanic fields
        for key, value in data.items():
            if hasattr(mechanic, key):
                setattr(mechanic, key, value)
        
        db.session.commit()
        
        result = mechanic_schema.dump(mechanic)
        return jsonify({
            'success': True,
            'message': 'Mechanic updated successfully',
            'data': result
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
@mechanic_token_required
def delete_mechanic(current_mechanic_id, mechanic_id):
    """Delete mechanic"""
    try:
        if current_mechanic_id != mechanic_id:
            return jsonify({
                'success': False,
                'error': 'Not authorized to delete this mechanic'
            }), 403
        
        mechanic = Mechanic.query.get(mechanic_id)
        
        if not mechanic:
            return jsonify({
                'success': False,
                'error': f'Mechanic with id {mechanic_id} not found'
            }), 404
        
        # Store mechanic info before deletion for the message
        mechanic_info = f"{mechanic.first_name} {mechanic.last_name}"
        
        db.session.delete(mechanic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mechanic {mechanic_info} (ID: {mechanic_id}) deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500