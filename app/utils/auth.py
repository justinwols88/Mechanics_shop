"""
Authentication utilities for Mechanics Shop API - FIXED for PyJWT
"""
import os
from functools import wraps
from flask import request, jsonify
import jwt  # Using PyJWT instead of python-jose
from datetime import datetime, timezone

# Use environment variable with fallback
SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def token_required(f):
    """Decorator for customer token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if Authorization header exists
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                "success": False,
                "error": "Authentication required",
                "message": "No authorization header provided"
            }), 401

        # Validate Authorization header format
        parts = auth_header.split()
        
        if len(parts) != 2:
            return jsonify({
                "success": False,
                "error": "Invalid token format",
                "message": "Use: Bearer <token>"
            }), 401

        if parts[0].lower() != 'bearer':
            return jsonify({
                "success": False,
                "error": "Invalid token format", 
                "message": "Use: Bearer <token>"
            }), 401

        token = parts[1]

        try:
            # Decode token using PyJWT
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Check token type
            if data.get('type') != 'customer':
                return jsonify({
                    "success": False,
                    "error": "Invalid token type",
                    "message": "Customer token required"
                }), 403
                
            customer_id = data['customer_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token expired",
                "message": "Please login again"
            }), 401
            
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": "Invalid token",
                "message": "Token is invalid"
            }), 401
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Token validation failed",
                "message": str(e)
            }), 401

        return f(customer_id, *args, **kwargs)

    return decorated

def mechanic_token_required(f):
    """Decorator for mechanic token authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if Authorization header exists
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                "success": False,
                "error": "Authentication required",
                "message": "No authorization header provided"
            }), 401

        # Validate Authorization header format
        parts = auth_header.split()
        
        if len(parts) != 2:
            return jsonify({
                "success": False,
                "error": "Invalid token format",
                "message": "Use: Bearer <token>"
            }), 401

        if parts[0].lower() != 'bearer':
            return jsonify({
                "success": False,
                "error": "Invalid token format", 
                "message": "Use: Bearer <token>"
            }), 401

        token = parts[1]

        try:
            # Decode token using PyJWT
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Check token type and role
            if data.get('type') != 'mechanic':
                return jsonify({
                    "success": False,
                    "error": "Invalid token type",
                    "message": "Mechanic token required"
                }), 403
                
            mechanic_id = data.get('mechanic_id')
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "error": "Token expired",
                "message": "Please login again"
            }), 401
            
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "error": "Invalid token",
                "message": "Token is invalid"
            }), 401
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "Token validation failed",
                "message": str(e)
            }), 401

        return f(mechanic_id, *args, **kwargs)

    return decorated