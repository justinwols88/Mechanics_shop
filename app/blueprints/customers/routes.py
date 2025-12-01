"""
Customer Routes with Consistent Authentication & Error Handling
"""
from flask import Blueprint, request, jsonify
from app.models.customer import Customer
from app.models.service_ticket import ServiceTicket
from app.utils.auth import token_required, mechanic_token_required
from app import db

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/register', methods=['POST'])
def register_customer():
    """Create a new customer - No auth required"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Check if email already exists
        if Customer.query.filter_by(email=data['email']).first():
            return jsonify({
                "success": False,
                "error": "Customer with this email already exists"
            }), 409

        # Create customer
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address')
        )
        customer.set_password(data['password'])

        db.session.add(customer)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Customer registered successfully",
            "customer": customer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@customers_bp.route('/', methods=['GET'])
@mechanic_token_required  # Only mechanics can view all customers
def get_all_customers(current_mechanic_id):
    """Get all customers with pagination - Mechanic auth required"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Validate pagination parameters
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({
                "success": False,
                "error": "Invalid pagination parameters"
            }), 400

        customers = Customer.query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            "success": True,
            "data": {
                "customers": [customer.to_dict() for customer in customers.items],
                "total": customers.total,
                "pages": customers.pages,
                "current_page": page,
                "per_page": per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@token_required  # Customers can only view their own profile
def get_customer(current_customer_id, customer_id):
    """Get a specific customer by ID - Customer auth required"""
    try:
        # Customers can only access their own data
        if current_customer_id != customer_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized access"
            }), 403

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({
                "success": False,
                "error": "Customer not found"
            }), 404

        return jsonify({
            "success": True,
            "data": customer.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(current_customer_id, customer_id):
    """Update a customer - Customer auth required (own profile only)"""
    try:
        # Customers can only update their own data
        if current_customer_id != customer_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized to update this customer"
            }), 403

        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({
                "success": False,
                "error": "Customer not found"
            }), 404

        data = request.get_json()

        # Update fields if provided
        updatable_fields = ['first_name', 'last_name', 'phone', 'address']
        for field in updatable_fields:
            if field in data:
                setattr(customer, field, data[field])

        # Special handling for email (unique constraint)
        if 'email' in data and data['email'] != customer.email:
            existing_customer = Customer.query.filter_by(email=data['email']).first()
            if existing_customer and existing_customer.id != customer.id:
                return jsonify({
                    "success": False,
                    "error": "Email already taken"
                }), 409
            customer.email = data['email']

        # Special handling for password
        if 'password' in data:
            customer.set_password(data['password'])

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Customer updated successfully",
            "data": customer.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_customer_id, customer_id):
    """Soft delete a customer"""
    try:
        if current_customer_id != customer_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized to delete this customer"
            }), 403

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({
                "success": False,
                "error": "Customer not found"
            }), 404

        # Soft delete - mark as inactive instead of hard delete
        customer.is_active = False
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Customer deactivated successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@customers_bp.route('/me/tickets', methods=['GET'])
@token_required
def get_my_tickets(current_customer_id):
    """Get the current customer's service tickets - Customer auth required"""
    try:
        customer = db.session.get(Customer, current_customer_id)
        if not customer:
            return jsonify({
                "success": False,
                "error": "Customer not found"
            }), 404

        # Get customer's tickets with proper error handling
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