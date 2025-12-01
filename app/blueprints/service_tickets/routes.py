"""
Service Tickets Routes
"""
from flask import Blueprint, request, jsonify
from app.models.service_ticket import ServiceTicket
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from app import db

service_tickets_bp = Blueprint('service_tickets', __name__)

@service_tickets_bp.route('/tickets', methods=['POST'])
def create_service_ticket():
    """Create a new service ticket"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['customer_id', 'vehicle_info', 'issue_description']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    
    # Check if customer exists
    customer = db.session.get(Customer, data['customer_id'])
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    # Create service ticket
    ticket = ServiceTicket(
        customer_id=data['customer_id'],
        vehicle_info=data['vehicle_info'],
        issue_description=data['issue_description'],
        status=data.get('status', 'open'),
        priority=data.get('priority', 'medium'),
        estimated_hours=data.get('estimated_hours', 0.0)
    )
    
    db.session.add(ticket)
    db.session.commit()
    
    return jsonify(ticket.to_dict()), 201

@service_tickets_bp.route('/tickets', methods=['GET'])
def get_all_service_tickets():
    """Get all service tickets with optional filtering"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = ServiceTicket.query
    
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    
    tickets = query.all()
    
    return jsonify({
        'tickets': [ticket.to_dict() for ticket in tickets],
        'count': len(tickets)
    }), 200

@service_tickets_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
    """Get a specific service ticket by ID"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    return jsonify(ticket.to_dict()), 200

@service_tickets_bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_service_ticket(ticket_id):
    """Update a service ticket"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    updatable_fields = ['vehicle_info', 'issue_description', 'status', 'priority', 
                       'estimated_hours', 'total_cost']
    
    for field in updatable_fields:
        if field in data:
            setattr(ticket, field, data[field])
    
    db.session.commit()
    
    return jsonify(ticket.to_dict()), 200

@service_tickets_bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_service_ticket(ticket_id):
    """Delete a service ticket"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    db.session.delete(ticket)
    db.session.commit()
    
    return jsonify({"message": "Service ticket deleted successfully"}), 200

@service_tickets_bp.route('/tickets/customer/<int:customer_id>', methods=['GET'])
def get_customer_tickets(customer_id):
    """Get all service tickets for a customer"""
    # Check if customer exists
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    
    return jsonify({
        'customer_id': customer_id,
        'tickets': [ticket.to_dict() for ticket in tickets],
        'count': len(tickets)
    }), 200

@service_tickets_bp.route('/tickets/<int:ticket_id>/assign-mechanic', methods=['POST'])
def assign_mechanic_to_ticket(ticket_id):
    """Assign a mechanic to a service ticket"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    data = request.get_json()
    mechanic_id = data.get('mechanic_id')
    
    if not mechanic_id:
        return jsonify({"error": "mechanic_id is required"}), 400
    
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    # Add mechanic to ticket (handle dynamic relationship collections)
    # Determine if mechanic is already assigned without using Python's `in` on relationship property
    if hasattr(ticket.mechanics, 'filter_by'):
        already_assigned = ticket.mechanics.filter_by(id=mechanic.id).first() is not None
    else:
        # Safely handle non-iterable relationship property for type checkers/runtime
        _mechs = getattr(ticket, 'mechanics', [])
        try:
            _mechs_iter = list(_mechs)
        except TypeError:
            _mechs_iter = []
        already_assigned = any(m.id == mechanic.id for m in _mechs_iter)
    if not already_assigned:
        ticket.mechanics.append(mechanic)
        db.session.commit()
    
    return jsonify({
        "message": f"Mechanic {mechanic.first_name} {mechanic.last_name} assigned to ticket",
        "ticket": ticket.to_dict()
    }), 200

@service_tickets_bp.route('/service_tickets/<int:ticket_id>/remove-mechanic', methods=['POST'])
def remove_mechanic_from_ticket(ticket_id):
    """Remove a mechanic from a service ticket"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    data = request.get_json()
    mechanic_id = data.get('mechanic_id')
    
    if not mechanic_id:
        return jsonify({"error": "mechanic_id is required"}), 400
    
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    # Remove mechanic from ticket (handle dynamic relationship collections)
    # Determine if mechanic is assigned without using Python's `in` on relationship property
    if hasattr(ticket.mechanics, 'filter_by'):
        assigned = ticket.mechanics.filter_by(id=mechanic.id).first() is not None
    else:
        # Safely handle non-iterable relationship property for type checkers/runtime
        _mechs = getattr(ticket, 'mechanics', [])
        try:
            _mechs_iter = list(_mechs)
        except TypeError:
            _mechs_iter = []
        assigned = any(m.id == mechanic.id for m in _mechs_iter)
    if assigned:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
    
    return jsonify({
        "message": f"Mechanic {mechanic.first_name} {mechanic.last_name} removed from ticket",
        "ticket": ticket.to_dict()
    }), 200

@service_tickets_bp.route('/service_tickets/<int:ticket_id>/add-part', methods=['POST'])
def add_part_to_ticket(ticket_id):
    """Add an inventory part to a service ticket"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    data = request.get_json()
    part_id = data.get('part_id')
    quantity = data.get('quantity', 1)
    
    if not part_id:
        return jsonify({"error": "part_id is required"}), 400
    
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Inventory part not found"}), 404
    
    # Add part to ticket (handle dynamic relationship collections; consider tracking quantity separately)
    # Determine if part is already added without using Python's `in` on relationship property
    if hasattr(ticket.inventory, 'filter_by'):
        already_added = ticket.inventory.filter_by(id=part.id).first() is not None
    else:
        # Safely handle non-iterable relationship property for type checkers/runtime
        _inv = getattr(ticket, 'inventory', [])
        try:
            _inv_iter = list(_inv)
        except TypeError:
            _inv_iter = []
        already_added = any(p.id == part.id for p in _inv_iter)
    if not already_added:
        ticket.inventory.append(part)
        
        # Update ticket cost
        ticket.total_cost = (ticket.total_cost or 0) + (part.price * quantity)
        
        db.session.commit()
    
    return jsonify({
        "message": f"Part {part.part_name} added to ticket",
        "ticket": ticket.to_dict()
    }), 200

@service_tickets_bp.route('/service_tickets/<int:ticket_id>/update-status', methods=['POST'])
def update_ticket_status(ticket_id):
    """Update service ticket status"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({"error": "status is required"}), 400
    
    valid_statuses = ['open', 'in_progress', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400
    
    ticket.status = new_status
    db.session.commit()
    
    return jsonify({
        "message": f"Ticket status updated to {new_status}",
        "ticket": ticket.to_dict()
    }), 200

@service_tickets_bp.route('/service_tickets/stats', methods=['GET'])
def get_ticket_stats():
    """Get service ticket statistics"""
    total_tickets = ServiceTicket.query.count()
    open_tickets = ServiceTicket.query.filter_by(status='open').count()
    in_progress_tickets = ServiceTicket.query.filter_by(status='in_progress').count()
    completed_tickets = ServiceTicket.query.filter_by(status='completed').count()
    
    return jsonify({
        'stats': {
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'in_progress_tickets': in_progress_tickets,
            'completed_tickets': completed_tickets,
            'completion_rate': (completed_tickets / total_tickets * 100) if total_tickets > 0 else 0
        }
    }), 200

@service_tickets_bp.route('/service_tickets/priority/<priority>', methods=['GET'])
def get_tickets_by_priority(priority):
    """Get service tickets by priority"""
    valid_priorities = ['low', 'medium', 'high', 'urgent']
    if priority not in valid_priorities:
        return jsonify({"error": f"Invalid priority. Must be one of: {valid_priorities}"}), 400
    
    tickets = ServiceTicket.query.filter_by(priority=priority).all()
    
    return jsonify({
        'priority': priority,
        'tickets': [ticket.to_dict() for ticket in tickets],
        'count': len(tickets)
    }), 200

@service_tickets_bp.route('/service_tickets/status/<status>', methods=['GET'])
def get_tickets_by_status(status):
    """Get service tickets by status"""
    valid_statuses = ['open', 'in_progress', 'completed', 'cancelled']
    if status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400
    
    tickets = ServiceTicket.query.filter_by(status=status).all()
    
    return jsonify({
        'status': status,
        'tickets': [ticket.to_dict() for ticket in tickets],
        'count': len(tickets)
    }), 200