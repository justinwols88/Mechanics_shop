"""
Mechanics Routes - Fixed endpoints
"""
from flask import Blueprint, request, jsonify
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket
from app.utils.auth import mechanic_token_required
from app import db

mechanics_bp = Blueprint('mechanics', __name__)

@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    """Get all mechanics - No auth required"""
    try:
        mechanics = Mechanic.query.all()
        return jsonify({
            "success": True,
            "data": {
                "mechanics": [mechanic.to_dict() for mechanic in mechanics],
                "count": len(mechanics)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@mechanics_bp.route('/register', methods=['POST'])
def create_mechanic():
    """Create a new mechanic - No auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Check if email already exists
        if Mechanic.query.filter_by(email=data['email']).first():
            return jsonify({
                "success": False,
                "error": "Mechanic with this email already exists"
            }), 409
        
        # Create mechanic
        mechanic = Mechanic(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            specialization=data.get('specialization'),
            years_experience=data.get('years_experience', 0),
            hourly_rate=data.get('hourly_rate', 0.0)
        )
        mechanic.set_password(data['password'])
        
        db.session.add(mechanic)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Mechanic created successfully",
            "data": mechanic.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    """Get a specific mechanic by ID - No auth required"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({
                "success": False,
                "error": "Mechanic not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": mechanic.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
@mechanic_token_required
def update_mechanic(current_mechanic_id, mechanic_id):
    """Update a mechanic - Mechanic auth required"""
    try:
        # Mechanics can only update their own profile
        if current_mechanic_id != mechanic_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized to update this mechanic"
            }), 403

        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({
                "success": False,
                "error": "Mechanic not found"
            }), 404
        
        data = request.get_json()
        
        # Update fields if provided
        updatable_fields = ['first_name', 'last_name', 'specialization', 
                           'years_experience', 'hourly_rate', 'is_active']
        for field in updatable_fields:
            if field in data:
                setattr(mechanic, field, data[field])

        # Special handling for email (unique constraint)
        if 'email' in data and data['email'] != mechanic.email:
            existing_mechanic = Mechanic.query.filter_by(email=data['email']).first()
            if existing_mechanic and existing_mechanic.id != mechanic.id:
                return jsonify({
                    "success": False,
                    "error": "Email already taken"
                }), 409
            mechanic.email = data['email']

        # Special handling for password
        if 'password' in data:
            mechanic.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Mechanic updated successfully",
            "data": mechanic.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(current_mechanic_id, mechanic_id):
    """Delete a mechanic - Mechanic auth required"""
    try:
        # Mechanics can only delete their own account
        if current_mechanic_id != mechanic_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized to delete this mechanic"
            }), 403

        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({
                "success": False,
                "error": "Mechanic not found"
            }), 404
        
        db.session.delete(mechanic)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Mechanic deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@mechanics_bp.route('/ranking', methods=['GET'])
def get_mechanics_ranking():
    """Get mechanics ranked by number of assigned service tickets - No auth required"""
    try:
        mechanics = Mechanic.query.all()
        
        ranking = []
        for mechanic in mechanics:
            ticket_count = len(mechanic.service_tickets) if hasattr(mechanic, 'service_tickets') else 0
            ranking.append({
                'id': mechanic.id,
                'name': f"{mechanic.first_name} {mechanic.last_name}",
                'email': mechanic.email,
                'specialization': mechanic.specialization,
                'ticket_count': ticket_count,
                'years_experience': mechanic.years_experience
            })
        
        # Sort by ticket count descending
        ranking.sort(key=lambda x: x['ticket_count'], reverse=True)
        
        return jsonify({
            "success": True,
            "data": {
                "ranking": ranking
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@mechanics_bp.route('/<int:mechanic_id>/tickets', methods=['GET'])
def get_mechanic_tickets(mechanic_id):
    """Get all service tickets assigned to a mechanic - No auth required"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({
                "success": False,
                "error": "Mechanic not found"
            }), 404
        
        tickets = mechanic.service_tickets if hasattr(mechanic, 'service_tickets') else []
        return jsonify({
            "success": True,
            "data": {
                "mechanic_id": mechanic_id,
                "tickets": [ticket.to_dict() for ticket in tickets],
                "count": len(tickets)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500