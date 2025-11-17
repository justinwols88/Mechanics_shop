from flask import Blueprint, jsonify, request
from app.models import ServiceTicket, Mechanic, Inventory, Customer
from app.extensions import db
from app.utils.auth import token_required, mechanic_token_required
from marshmallow import Schema, fields
from app.extensions import limiter, cache
from app.schemas import ServiceTicketSchema


service_tickets_bp = Blueprint('service_tickets', __name__)

@service_tickets_bp.route('/my-tickets' , methods=['GET'])
@token_required
def my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify([{"id": t.id, "description": t.description} for t in tickets])

@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket(ticket_id):
    data = request.get_json()
    ticket = ServiceTicket.query.get(ticket_id)
    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404
    if 'add_ids' in data:
        for mid in data['add_ids']:
            mechanic = Mechanic.query.get(mid)
            if mechanic:
                ticket.mechanics.append(mechanic)
    if 'remove_ids' in data:
        for mid in data['remove_ids']:
            mechanic = Mechanic.query.get(mid)
            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)
    db.session.commit()
    return jsonify({"message": "Ticket updated"})

@service_tickets_bp.route('/<int:ticket_id>/add-part', methods=['POST'])
def add_part_to_ticket(ticket_id):
    data = request.get_json()
    part_id = data.get('part_id')
    ticket = ServiceTicket.query.get(ticket_id)
    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404
    part = Inventory.query.get(part_id)
    if not part:
        return jsonify({"message": "Part not found"}), 404
    ticket.inventory.append(part)
    db.session.commit()
    return jsonify({"message": f"Part {part.name} added to ticket {ticket.id}"}
    )

@service_tickets_bp.route('', methods=['POST'])
@token_required  # If authentication is required
def create_service_ticket(current_user_id):
    """Create a new service ticket"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('customer_id') or not data.get('description'):
            return jsonify({
                'success': False,
                'error': 'customer_id and description are required'
            }), 400
        
        # Check if customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Create new service ticket
        new_ticket = ServiceTicket()
        new_ticket.customer_id = data['customer_id']
        new_ticket.description = data['description']
        new_ticket.status = data.get('status', 'open')
        
        db.session.add(new_ticket)
        db.session.commit()
        
        # Add mechanics if provided
        if 'mechanic_ids' in data:
            for mechanic_id in data['mechanic_ids']:
                mechanic = Mechanic.query.get(mechanic_id)
                if mechanic:
                    new_ticket.mechanics.append(mechanic)
            db.session.commit()
        
        result = ServiceTicketSchema().dump(new_ticket)
        return jsonify({
            'success': True,
            'message': 'Service ticket created successfully',
            'data': result
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@service_tickets_bp.route('', methods=['GET'])
@token_required
@cache.cached(timeout=30)
@limiter.limit("50 per minute")
def get_all_service_tickets(current_user_id):
    """Get all service tickets with auth, caching, and rate limiting"""
    try:
        tickets = ServiceTicket.query.all()
        result = ServiceTicketSchema(many=True).dump(tickets)
        
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
    

@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@token_required
@cache.cached(timeout=30, query_string=True)
@limiter.limit("30 per minute")
def get_service_ticket(current_user_id, ticket_id):
    """Get service ticket with auth, caching, and rate limiting"""
    try:
        ticket = ServiceTicket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': f'Service ticket with id {ticket_id} not found'
            }), 404
        
        # Optional authorization check
        # if ticket.customer_id != current_user_id:
        #     return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
        result = ServiceTicketSchema().dump(ticket)
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@mechanic_token_required
@limiter.limit("10 per minute")  # Lower limit for delete operations
def delete_service_ticket(current_mechanic_id, ticket_id):
    """Delete service ticket with auth and rate limiting"""
    try:
        # Get current mechanic for additional checks
        current_mechanic = Mechanic.query.get(current_mechanic_id)
        
        ticket = ServiceTicket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': f'Service ticket with id {ticket_id} not found'
            }), 404
        
        # Optional: Check if mechanic has admin role (if you implement roles)
        # if not getattr(current_mechanic, 'is_admin', False):
        #     return jsonify({
        #         'success': False,
        #         'error': 'Admin privileges required to delete service tickets'
        #     }), 403
        
        # Business rules for deletion
        allowed_statuses = ['open', 'cancelled']
        if ticket.status not in allowed_statuses:
            return jsonify({
                'success': False,
                'error': f'Cannot delete service ticket with status: {ticket.status}',
                'allowed_statuses': allowed_statuses,
                'current_status': ticket.status
            }), 400
        
        # Store ticket info for response message
        ticket_info = f"Ticket #{ticket_id} - {ticket.description[:50]}..."
        
        db.session.delete(ticket)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Service ticket {ticket_info} deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
