from flask import request, jsonify
from app.service_ticket import service_ticket_bp
from app.models import ServiceTicket, Mechanic
from app import db, limiter, cache
from app.service_ticket.schemas import service_ticket_schema, service_tickets_schema

@service_ticket_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting: 10 requests per minute
def create_service_ticket():
    """
    RATE LIMITED: 10 requests per minute
    Why: Creating service tickets is a common operation, but we want to prevent
    spam or automated ticket creation that could overwhelm the system.
    """
    try:
        data = request.get_json()
        
        errors = service_ticket_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        service_ticket = service_ticket_schema.load(data)
        db.session.add(service_ticket)
        db.session.commit()
        
        # Clear cache when new data is added
        cache.delete('all_service_tickets')
        
        return service_ticket_schema.jsonify(service_ticket), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@service_ticket_bp.route('/', methods=['GET'])
@cache.cached(timeout=30, key_prefix='all_service_tickets')  # Cache for 30 seconds
def get_service_tickets():
    """
    CACHED: 30 seconds
    Why: Service tickets are frequently accessed but can change more often than mechanics.
    Shorter cache timeout ensures users see recent updates while still reducing database load.
    """
    try:
        service_tickets = ServiceTicket.query.all()
        return service_tickets_schema.jsonify(service_tickets)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("20 per minute")  # Rate limiting: 20 requests per minute
def assign_mechanic(ticket_id, mechanic_id):
    """
    RATE LIMITED: 20 requests per minute
    Why: Assigning mechanics might happen frequently during busy periods,
    but we want to prevent automated assignment loops or abuse.
    """
    try:
        service_ticket = ServiceTicket.query.get_or_404(ticket_id)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        if mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
            db.session.commit()
            
            # Clear cache when assignments change
            cache.delete('all_service_tickets')
        
        return service_ticket_schema.jsonify(service_ticket)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("20 per minute")  # Rate limiting: 20 requests per minute
def remove_mechanic(ticket_id, mechanic_id):
    """
    RATE LIMITED: 20 requests per minute
    Why: Similar to assignment, removing mechanics should be controlled
    to prevent rapid changes that could indicate issues or abuse.
    """
    try:
        service_ticket = ServiceTicket.query.get_or_404(ticket_id)
        mechanic = Mechanic.query.get_or_404(mechanic_id)
        
        if mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
            db.session.commit()
            
            # Clear cache when assignments change
            cache.delete('all_service_tickets')
        
        return service_ticket_schema.jsonify(service_ticket)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
