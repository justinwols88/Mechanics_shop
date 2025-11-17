from flask import Blueprint, request, jsonify
from app.extensions import limiter, cache, db
from app.models import Customer
from app.schemas import CustomerSchema, LoginSchema
from app.utils.auth import encode_token

customers_bp = Blueprint('customers', __name__)
customer_schema = CustomerSchema()
login_schema = LoginSchema()


@customers_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400
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

    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({"message": "Email and password are required"}), 400

    # Check if email already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 409

    # Create new customer
    new_customer = Customer()
    new_customer.email = data['email']
    new_customer.password = data['password']
    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.dump(new_customer), 201

@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    return CustomerSchema().dump(customer), 200

@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    data = request.get_json()
    if 'email' in data:
        customer.email = data['email']
    if 'password' in data:
        customer.password = data['password']

    db.session.commit()
    return CustomerSchema().dump(customer), 200

from app.utils.auth import token_required
from app.models import ServiceTicket

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
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {id} deleted successfully"}), 200
