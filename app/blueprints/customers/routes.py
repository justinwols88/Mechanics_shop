"""
Customer Routes
"""
from flask import Blueprint, request, jsonify
from app.models.customer import Customer
from app import db
import jwt
from config import Config

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new customer"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    
    # Check if email already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Customer with this email already exists"}), 409
    
    # Create customer
    customer = Customer(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email']
    )
    customer.set_password(data['password'])
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(customer.to_dict()), 201

@customers_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    customers = Customer.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'customers': [customer.to_dict() for customer in customers.items],
        'total': customers.total,
        'pages': customers.pages,
        'current_page': page
    }), 200

@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID"""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    return jsonify(customer.to_dict()), 200

@customers_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update a customer"""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'first_name' in data:
        customer.first_name = data['first_name']
    if 'last_name' in data:
        customer.last_name = data['last_name']
    if 'email' in data and data['email'] != customer.email:
        # Check if new email is already taken
        existing = Customer.query.filter_by(email=data['email']).first()
        if existing and existing.id != customer.id:
            return jsonify({"error": "Email already taken"}), 409
        customer.email = data['email']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'address' in data:
        customer.address = data['address']
    
    db.session.commit()
    
    return jsonify(customer.to_dict()), 200

@customers_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer"""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({"message": "Customer deleted successfully"}), 200

@customers_bp.route('/customers/me/tickets', methods=['GET'])
def get_my_tickets():
    """Get the current customer's service tickets"""
    # Check for authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authentication required"}), 401
    
    # For now, return an empty array since we don't have full ticket implementation
    # In a real implementation, you would:
    # 1. Validate the JWT token
    # 2. Get the customer ID from the token
    # 3. Query the service_tickets table for that customer
    return jsonify({"tickets": []}), 200

