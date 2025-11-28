"""
Service Tickets Routes
"""
from flask import Blueprint, request, jsonify
from app.models.service_ticket import ServiceTicket
from ...models.service_ticket import ServiceTicket
from app import db

service_tickets_bp = Blueprint('service_tickets', __name__)

@service_tickets_bp.route('/service_tickets', methods=['POST'])
def create_service_ticket():
    """Create a new service ticket"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['customer_id', 'vehicle_info', 'issue_description']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # Create service ticket
    ticket = ServiceTicket(
        customer_id=data['customer_id'],
        vehicle_info=data['vehicle_info'],
        issue_description=data['issue_description'],
        status=data.get('status', 'open'),
        priority=data.get('priority', 'medium')
    )

    db.session.add(ticket)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201

@service_tickets_bp.route('/service_tickets/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
    """Get a specific service ticket by ID"""
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    return jsonify(ticket.to_dict()), 200

@service_tickets_bp.route('/service_tickets/customer/<int:customer_id>', methods=['GET'])
def get_customer_tickets(customer_id):
    """Get all service tickets for a customer"""
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify({
        'tickets': [ticket.to_dict() for ticket in tickets]
    }), 200
