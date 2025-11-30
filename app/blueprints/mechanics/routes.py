"""
Mechanics Routes
"""
from flask import Blueprint, request, jsonify
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket
from app import db

mechanics_bp = Blueprint('mechanics', __name__)

@mechanics_bp.route('/mechanics', methods=['GET'])
def get_mechanics():
    """Get all mechanics"""
    mechanics = Mechanic.query.all()
    return jsonify({
        'mechanics': [mechanic.to_dict() for mechanic in mechanics]
    }), 200

@mechanics_bp.route('/mechanics', methods=['POST'])
def create_mechanic():
    """Create a new mechanic"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    
    # Check if email already exists
    if Mechanic.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Mechanic with this email already exists"}), 409
    
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
    
    return jsonify(mechanic.to_dict()), 201

@mechanics_bp.route('/mechanics/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    """Get a specific mechanic by ID"""
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    return jsonify(mechanic.to_dict()), 200

@mechanics_bp.route('/mechanics/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    """Update a mechanic"""
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'first_name' in data:
        mechanic.first_name = data['first_name']
    if 'last_name' in data:
        mechanic.last_name = data['last_name']
    if 'email' in data and data['email'] != mechanic.email:
        # Check if new email is already taken
        existing = Mechanic.query.filter_by(email=data['email']).first()
        if existing and existing.id != mechanic.id:
            return jsonify({"error": "Email already taken"}), 409
        mechanic.email = data['email']
    if 'specialization' in data:
        mechanic.specialization = data['specialization']
    if 'years_experience' in data:
        mechanic.years_experience = data['years_experience']
    if 'hourly_rate' in data:
        mechanic.hourly_rate = data['hourly_rate']
    if 'is_active' in data:
        mechanic.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify(mechanic.to_dict()), 200

@mechanics_bp.route('/mechanics/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    """Delete a mechanic"""
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    
    return jsonify({"message": "Mechanic deleted successfully"}), 200

@mechanics_bp.route('/mechanics/ranking', methods=['GET'])
def get_mechanics_ranking():
    """Get mechanics ranked by number of assigned service tickets"""
    mechanics = Mechanic.query.all()
    
    ranking = []
    for mechanic in mechanics:
        ticket_count = len(mechanic.service_tickets)
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
        'ranking': ranking
    }), 200

@mechanics_bp.route('/mechanics/<int:mechanic_id>/tickets', methods=['GET'])
def get_mechanic_tickets(mechanic_id):
    """Get all service tickets assigned to a mechanic"""
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    tickets = mechanic.service_tickets
    return jsonify({
        'mechanic_id': mechanic_id,
        'tickets': [ticket.to_dict() for ticket in tickets]
    }), 200

@mechanics_bp.route('/mechanics/<int:mechanic_id>/active-tickets', methods=['GET'])
def get_mechanic_active_tickets(mechanic_id):
    """Get active service tickets assigned to a mechanic"""
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    active_tickets = [ticket for ticket in mechanic.service_tickets if ticket.status in ['open', 'in_progress']]
    
    return jsonify({
        'mechanic_id': mechanic_id,
        'active_tickets': [ticket.to_dict() for ticket in active_tickets],
        'active_count': len(active_tickets)
    }), 200

@mechanics_bp.route('/mechanics/specialization/<specialization>', methods=['GET'])
def get_mechanics_by_specialization(specialization):
    """Get mechanics by specialization"""
    mechanics = Mechanic.query.filter_by(specialization=specialization).all()
    
    return jsonify({
        'specialization': specialization,
        'mechanics': [mechanic.to_dict() for mechanic in mechanics],
        'count': len(mechanics)
    }), 200

@mechanics_bp.route('/mechanics/available', methods=['GET'])
def get_available_mechanics():
    """Get available mechanics (not assigned to many active tickets)"""
    mechanics = Mechanic.query.filter_by(is_active=True).all()
    
    available_mechanics = []
    for mechanic in mechanics:
        active_ticket_count = len([ticket for ticket in mechanic.service_tickets if ticket.status in ['open', 'in_progress']])
        
        # Consider a mechanic available if they have less than 3 active tickets
        if active_ticket_count < 3:
            available_mechanics.append({
                **mechanic.to_dict(),
                'active_ticket_count': active_ticket_count
            })
    
    return jsonify({
        'available_mechanics': available_mechanics,
        'count': len(available_mechanics)
    }), 200