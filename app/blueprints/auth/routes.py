"""
Authentication Routes with Enhanced Error Handling
"""
from flask import Blueprint, request, jsonify
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/customer/login', methods=['POST'])
def customer_login():
    """Customer login endpoint with comprehensive error handling"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        data = request.get_json()

        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "success": False,
                "error": "Email and password are required"
            }), 400

        # Find customer
        customer = Customer.query.filter_by(email=data['email']).first()

        if not customer:
            return jsonify({
                "success": False,
                "error": "Invalid credentials"
            }), 401

        if not customer.check_password(data['password']):
            return jsonify({
                "success": False,
                "error": "Invalid credentials"
            }), 401

        # Generate token
        token = customer.generate_token()
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "customer": customer.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500

@auth_bp.route('/mechanic/login', methods=['POST'])
def mechanic_login():
    """Mechanic login endpoint with comprehensive error handling"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Missing JSON in request"
            }), 400

        data = request.get_json()

        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "success": False,
                "error": "Email and password are required"
            }), 400

        # Find mechanic
        mechanic = Mechanic.query.filter_by(email=data['email']).first()

        if not mechanic:
            return jsonify({
                "success": False,
                "error": "Invalid credentials"
            }), 401

        if not mechanic.check_password(data['password']):
            return jsonify({
                "success": False,
                "error": "Invalid credentials"
            }), 401

        # Generate token
        token = mechanic.generate_token()
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "mechanic": mechanic.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500