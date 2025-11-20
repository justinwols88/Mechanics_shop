from flask import Blueprint, request, jsonify
from app.extensions import limiter, cache, db
from app.models import Customer, ServiceTicket
from app.schemas import CustomerSchema, LoginSchema
from app.utils.auth import encode_token, token_required
import re

customers_bp = Blueprint('customers_bp', __name__)
customer_schema = CustomerSchema()
login_schema = LoginSchema()

@customers_bp.route('/')
def index():
    return "Customers page"

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_customer_data(data, is_update=False):
    """Validate customer input data"""
    errors = []
    
    if not is_update:
        # For registration, both email and password are required
        if 'email' not in data or not data['email']:
            errors.append("Email is required")
        elif not validate_email(data['email']):
            errors.append("Invalid email format")
        
        if 'password' not in data or not data['password']:
            errors.append("Password is required")
        elif len(data['password']) < 6:
            errors.append("Password must be at least 6 characters long")
    else:
        # For updates, validate only provided fields
        if 'email' in data and data['email']:
            if not validate_email(data['email']):
                errors.append("Invalid email format")
        
        if 'password' in data and data['password'] and len(data['password']) < 6:
            errors.append("Password must be at least 6 characters long")
    
    return errors

@customers_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400
        
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400
        
    # Additional validation
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400
    
    customer = Customer.query.filter_by(email=data['email']).first()
    if customer and customer.password == data['password']:
        token = encode_token(customer.id)
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

@customers_bp.route('/all')
@limiter.limit("10 per minute")
@cache.cached(timeout=60)
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10

    customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "page": customers.page,
        "per_page": customers.per_page,
        "total": customers.total,
        "pages": customers.pages,
        "customers": CustomerSchema(many=True).dump(customers.items)
    })

@customers_bp.route('/register', methods=['POST'])
def register_customer():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    # Validate input data
    validation_errors = validate_customer_data(data, is_update=False)
    if validation_errors:
        return jsonify({
            "message": "Validation failed",
            "errors": validation_errors
        }), 400

    # Check if email already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409

    # Create new customer
    try:
        new_customer = Customer()
        new_customer.email = data['email']
        new_customer.password = data['password']
        db.session.add(new_customer)
        db.session.commit()

        return customer_schema.dump(new_customer), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error creating customer",
            "error": str(e)
        }), 500

@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    return CustomerSchema().dump(customer), 200

@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400

    # Validate input data
    validation_errors = validate_customer_data(data, is_update=True)
    if validation_errors:
        return jsonify({
            "message": "Validation failed",
            "errors": validation_errors
        }), 400

    # Update fields
    try:
        if 'email' in data:
            # Check if new email already exists (excluding current customer)
            existing = Customer.query.filter(
                Customer.email == data['email'],
                Customer.id != id
            ).first()
            if existing:
                return jsonify({"message": "Email already registered"}), 409
            customer.email = data['email']
            
        if 'password' in data:
            customer.password = data['password']

        db.session.commit()
        return CustomerSchema().dump(customer), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error updating customer",
            "error": str(e)
        }), 500

@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify([
        {"id": t.id, "description": t.description}
        for t in tickets
    ]), 200

@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f"Customer {id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": "Error deleting customer",
            "error": str(e)
        }), 500