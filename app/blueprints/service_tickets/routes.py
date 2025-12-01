"""
Service Tickets Routes - FIXED with proper authentication and error handling
"""
from flask import Blueprint, request, jsonify
from app.models.service_ticket import ServiceTicket
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from app.utils.auth import token_required, mechanic_token_required
from app import db

service_tickets_bp = Blueprint('service_tickets', __name__)

@service_tickets_bp.route('/', methods=['POST'])
@token_required
def create_service_ticket(current_customer_id):
    """Create a new service ticket - Customer auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['vehicle_info', 'issue_description']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Create service ticket with authenticated customer's ID
        ticket = ServiceTicket(
            customer_id=current_customer_id,  # Use authenticated customer's ID
            vehicle_info=data['vehicle_info'],
            issue_description=data['issue_description'],
            status=data.get('status', 'open'),
            priority=data.get('priority', 'medium'),
            estimated_hours=data.get('estimated_hours', 0.0)
        )

        db.session.add(ticket)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Service ticket created successfully",
            "data": ticket.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@service_tickets_bp.route('/', methods=['GET'])
@mechanic_token_required
def get_all_service_tickets(_current_mechanic_id):
    """Get all service tickets - Mechanic auth required"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        query = ServiceTicket.query
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        
        tickets = query.all()
        
        return jsonify({
            "success": True,
            "data": {
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

@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@token_required
def get_service_ticket(current_customer_id, ticket_id):
    """Get a specific service ticket by ID - Customer auth required"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({
                "success": False,
                "error": "Service ticket not found"
            }), 404

        # Customers can only access their own tickets
        if ticket.customer_id != current_customer_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized access"
            }), 403

        return jsonify({
            "success": True,
            "data": ticket.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@service_tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@token_required
def update_service_ticket(current_customer_id, ticket_id):
    """Update a service ticket - Customer auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({
                "success": False,
                "error": "Service ticket not found"
            }), 404

        # Customers can only update their own tickets
        if ticket.customer_id != current_customer_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized to update this ticket"
            }), 403

        data = request.get_json()
        
        # Update fields if provided (don't allow customer_id updates)
        updatable_fields = ['vehicle_info', 'issue_description', 'status', 'priority', 
                           'estimated_hours', 'total_cost']
        
        for field in updatable_fields:
            if field in data:
                setattr(ticket, field, data[field])

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Service ticket updated successfully",
            "data": ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@mechanic_token_required
def delete_service_ticket(current_mechanic_id, ticket_id):
    """Delete a service ticket - Mechanic auth required"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({
                "success": False,
                "error": "Service ticket not found"
            }), 404

        db.session.delete(ticket)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Service ticket deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@service_tickets_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(current_customer_id):
    """Get the current customer's service tickets - Customer auth required"""
    try:
        tickets = ServiceTicket.query.filter_by(customer_id=current_customer_id).all()
        
        return jsonify({
            "success": True,
            "data": {
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

@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic', methods=['POST'])
@mechanic_token_required
def assign_mechanic_to_ticket(current_mechanic_id, ticket_id):
    """Assign a mechanic to a service ticket - Mechanic auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({
                "success": False,
                "error": "Service ticket not found"
            }), 404

        data = request.get_json()
        mechanic_id = data.get('mechanic_id', current_mechanic_id)  # Default to current mechanic

        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({
                "success": False,
                "error": "Mechanic not found"
            }), 404

        # Add mechanic to ticket if not already assigned (supports dynamic relationships)
        already_assigned = getattr(ticket.mechanics, 'filter_by', None)
        if callable(already_assigned):
            exists = ticket.mechanics.filter_by(id=mechanic.id).first() is not None
        else:
            # Safely handle non-queryable relationship collections and RelationshipProperty
            try:
                collection = getattr(ticket, 'mechanics')
                # If it's a list-like collection
                if isinstance(collection, list):
                    exists = any(getattr(m, 'id', None) == mechanic.id for m in collection)
                else:
                    # Fallback: explicit DB check via join to avoid "in" on RelationshipProperty
                    exists = db.session.query(Mechanic).join(Mechanic.service_tickets).\
                        filter(ServiceTicket.id == ticket.id, Mechanic.id == mechanic.id).first() is not None
            except Exception:
                exists = db.session.query(Mechanic).join(Mechanic.service_tickets).\
                    filter(ServiceTicket.id == ticket.id, Mechanic.id == mechanic.id).first() is not None

        if not exists:
            ticket.mechanics.append(mechanic)
            db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Mechanic {mechanic.first_name} {mechanic.last_name} assigned to ticket",
            "data": ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@service_tickets_bp.route('/<int:ticket_id>/add-part', methods=['POST'])
@mechanic_token_required
def add_part_to_ticket(current_mechanic_id, ticket_id):
    """Add an inventory part to a service ticket - Mechanic auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({
                "success": False,
                "error": "Service ticket not found"
            }), 404

        data = request.get_json()
        part_id = data.get('part_id')
        quantity = data.get('quantity', 1)

        if not part_id:
            return jsonify({
                "success": False,
                "error": "part_id is required"
            }), 400

        part = db.session.get(Inventory, part_id)
        if not part:
            return jsonify({
                "success": False,
                "error": "Inventory part not found"
            }), 404

        # Check if part is already in stock
        if part.quantity < quantity:
            return jsonify({
                "success": False,
                "error": f"Not enough inventory. Only {part.quantity} available"
            }), 400

        # Add part to ticket if not already added (supports dynamic relationships)
        # Determine if the part is already associated with the ticket, handling
        # both dynamic relationships (queryable) and normal list relationships
        inv_exists = False
        try:
            # Dynamic relationship returns a query-like object
            inv_query_like = getattr(ticket.inventory, 'filter_by', None)
            if callable(inv_query_like):
                inv_exists = ticket.inventory.filter_by(id=part.id).first() is not None
            else:
                # If it's a list-like collection, iterate safely
                inv_collection = getattr(ticket, 'inventory', [])
                if isinstance(inv_collection, list):
                    inv_exists = any(getattr(p, 'id', None) == part.id for p in inv_collection)
                else:
                    # Final fallback: explicit DB check via join
                    inv_exists = db.session.query(Inventory).join(Inventory.service_tickets).\
                        filter(ServiceTicket.id == ticket.id, Inventory.id == part.id).first() is not None
        except Exception:
            # If any unexpected type issue occurs, do a safe DB check
            inv_exists = db.session.query(Inventory).join(Inventory.service_tickets).\
                filter(ServiceTicket.id == ticket.id, Inventory.id == part.id).first() is not None

        if not inv_exists:
            ticket.inventory.append(part)
            
            # Update inventory quantity
            part.quantity -= quantity
            
            # Update ticket cost
            ticket.total_cost = (ticket.total_cost or 0) + (part.price * quantity)
            
            db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Part {part.part_name} added to ticket",
            "data": ticket.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500