from functools import wraps
from flask import request, jsonify, current_app
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
import os

SECRET_KEY = os.environ.get("SUPER_SECRET_KEY")

def encode_token(customer_id):
    payload = {"customer_id": customer_id}
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header exists
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            # Validate Authorization header format
            parts = auth_header.split()
            
            # Should have exactly 2 parts: "Bearer" and the token
            if len(parts) != 2:
                return jsonify({"message": "Invalid token format. Use: Bearer <token>"}), 401
            
            # Should start with "Bearer"
            if parts[0].lower() != 'bearer':
                return jsonify({"message": "Invalid token format. Use: Bearer <token>"}), 401
            
            token = parts[1]
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            customer_id = data['customer_id']
        except ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except JWTError:
            return jsonify({"message": "Token is invalid"}), 401
        except Exception:
            return jsonify({"message": "Token is invalid"}), 401
        
        return f(customer_id, *args, **kwargs)
    return decorated

def encode_mechanic_token(mechanic_id):
    payload = {"mechanic_id": mechanic_id, "role": "mechanic"}
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header exists
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            # Validate Authorization header format
            parts = auth_header.split()
            
            # Should have exactly 2 parts: "Bearer" and the token
            if len(parts) != 2:
                return jsonify({"message": "Invalid token format. Use: Bearer <token>"}), 401
            
            # Should start with "Bearer"
            if parts[0].lower() != 'bearer':
                return jsonify({"message": "Invalid token format. Use: Bearer <token>"}), 401
            
            token = parts[1]
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Check if token has mechanic role
            if data.get('role') != 'mechanic':
                return jsonify({"message": "Unauthorized - Mechanic token required"}), 403
            
            mechanic_id = data['mechanic_id']
        except ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except JWTError:
            return jsonify({"message": "Token is invalid"}), 401
        except Exception:
            return jsonify({"message": "Token is invalid"}), 401
        
        return f(mechanic_id, *args, **kwargs)
    return decorated
