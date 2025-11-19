from flask import Blueprint, jsonify, request
from app.models import ServiceTicket, Mechanic, Inventory, Customer
from app.extensions import db
from app.utils.auth import token_required, mechanic_token_required
from app.schemas import ServiceTicketSchema
from app.extensions import limiter, cache

service_tickets_bp = Blueprint('service_tickets', __name__)

def validate_service_ticket_data(data, is_update=False):
    """Validate service ticket input data"""
    errors = []
    
    if not is_update:
        # For creation, customer_id and description are required
        if 'customer_id' not in data:
            errors.append("customer_id is required")
        else:
            try:
                customer_id = int(data['customer_id'])
                if customer_id <= 0:
                    errors.append("customer_id must be a positive integer")
            except (ValueError, TypeError):
                errors.append("customer_id must be a valid integer")
        
        if 'description' not in data or not data['description'] or not data['description'].strip():
            errors.append("description is required and cannot be empty")
        elif len(data['description'].strip()) > 1000:
            errors.append("description is too long (max 1000 characters)")
    
    # Validate status if provided
    if 'status' in data and data['status']:
        valid_statuses = ['open', 'in_progress', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            errors.append(f"status must be one of: {', '.join(valid_statuses)}")
    
    # Validate mechanic_ids if provided
    if 'mechanic_ids' in data and data['mechanic_ids']:
        if not isinstance(data['mechanic_ids'], list):
            errors.append("mechanic_ids must be an array")
        else:
            for mechanic_id in data['mechanic_ids']:
                try:
                    int(mechanic_id)
                except (ValueError, TypeError):
                    errors.append("mechanic_ids must contain valid integers")
                    break
    
    return errors

@service_tickets_bp.route('/my-tickets' , methods=['GET'])
@token_required
def my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify([{"id": t.id, "description": t.description} for t in tickets])

@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket(ticket_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404
    
    # Validate input data
    validation_errors = []
    
    if 'add_ids' in data and data['add_ids']:
        if not isinstance(data['add_ids'], list):
            validation_errors.append("add_ids must be an array")
        else:
            for mechanic_id in data['add_ids']:
                try:
                    int(mechanic_id)
                except (ValueError, TypeError):
                    validation_errors.append("add_ids must contain valid integers")
                    break
    
    if 'remove_ids' in data and data['remove_ids']:
        if not isinstance(data['remove_ids'], list):
            validation_errors.append("remove_ids must be an array")
        else:
            for mechanic_id in data['remove_ids']:
                try:
                    int(mechanic_id)
                except (ValueError, TypeError):
                    validation_errors.append("remove_ids must contain valid integers")
                    break
    
    if validation_errors:
        return jsonify({
            "message": "Validation failed",
            "errors": validation_errors
        }), 400
    
    # Process additions
    if 'add_ids' in data:
        for mid in data['add_ids']:
            mechanic = db.session.get(Mechanic, mid)
            if mechanic:
                # Materialize relationship into a list so type checkers see it as iterable
                current_mechanics = list(ticket.mechanics)  # type: ignore[arg-type]
                existing_ids = {m.id for m in current_mechanics}
                if mechanic.id not in existing_ids:
                    ticket.mechanics.append(mechanic)
    
    # Process removals
    if 'remove_ids' in data:
        for mid in data['remove_ids']:
            mechanic = db.session.get(Mechanic, mid)
            if mechanic:
                # Materialize mechanics into a list/slice so type checkers see it as iterable
                mechanics_on_ticket = ticket.mechanics[:]  # type: ignore[assignment]
                mech_on_ticket = next(
                    (m for m in mechanics_on_ticket if m.id == mechanic.id),
                    None
                )
                if mech_on_ticket is not None:
                    ticket.mechanics.remove(mech_on_ticket)
    
    db.session.commit()
    return jsonify({"message": "Ticket updated"})

@service_tickets_bp.route('/<int:ticket_id>/add-part', methods=['POST'])
def add_part_to_ticket(ticket_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    # Validate part_id
    if 'part_id' not in data:
        return jsonify({"message": "part_id is required"}), 400
    
    try:
        part_id = int(data['part_id'])
        if part_id <= 0:
            return jsonify({"message": "part_id must be a positive integer"}), 400
    except (ValueError, TypeError):
        return jsonify({"message": "part_id must be a valid integer"}), 400
    
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"message": "Ticket not found"}), 404
    
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"message": "Part not found"}), 404
    
    ticket.inventory.append(part)
    db.session.commit()
    return jsonify({
        "message": f"Part {part.id} added to ticket {ticket.id}"
    })

@service_tickets_bp.route('', methods=['POST'])
@token_required
def create_service_ticket(customers_id):
    """Create a new service ticket"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input data
        validation_errors = validate_service_ticket_data(data, is_update=False)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'details': validation_errors
            }), 400
        
        # Convert customer_id to integer after validation
        customer_id = int(data['customer_id'])
        
        # Check if customer exists
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Create new service ticket
        new_ticket = ServiceTicket()
        new_ticket.customer_id = customer_id
        new_ticket.description = data['description'].strip()
        new_ticket.status = data.get('status', 'open')
        
        db.session.add(new_ticket)
        db.session.commit()
        
        # Add mechanics if provided
        if 'mechanic_ids' in data and data['mechanic_ids']:
            for mechanic_id in data['mechanic_ids']:
                mechanic = db.session.get(Mechanic, mechanic_id)
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
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': f'Service ticket with id {ticket_id} not found'
            }), 404
        
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
@limiter.limit("10 per minute")
def delete_service_ticket(current_mechanic_id, ticket_id):
    """Delete service ticket with auth and rate limiting"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': f'Service ticket with id {ticket_id} not found'
            }), 404
        
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