"""
Authentication Routes
"""
from flask import Blueprint, request, jsonify
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/customer/login', methods=['POST'])
def customer_login():
    """Customer login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400
    
    customer = Customer.query.filter_by(email=data['email']).first()
    
    if not customer or not customer.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = customer.generate_token()
    return jsonify({
        "token": token,
        "customer": customer.to_dict()
    }), 200

@auth_bp.route('/auth/mechanic/login', methods=['POST'])
def mechanic_login():
    """Mechanic login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password required"}), 400
    
    mechanic = Mechanic.query.filter_by(email=data['email']).first()
    
    if not mechanic or not mechanic.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = mechanic.generate_token()
    return jsonify({
        "token": token,
        "mechanic": mechanic.to_dict()
    }), 200
