"""
Authentication utilities for Mechanics Shop API
"""

import os
from flask import request, jsonify
from jose import jwt

# JWTError imported below, ExpiredSignatureError
from functools import wraps

# Use environment variable with fallback for CI/CD
SECRET_KEY = os.environ.get("SECRET_KEY") or "super secret secrets"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def encode_token(customer_id):
    payload = {"customer_id": customer_id}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if Authorization header exists
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]

            # Validate Authorization header format
            parts = auth_header.split()

            # Should have exactly 2 parts: "Bearer" and the token
            if len(parts) != 2:
                return (
                    jsonify({"message": "Invalid token format. Use: Bearer <token>"}),
                    401,
                )

            # Should start with "Bearer"
            if parts[0].lower() != "bearer":
                return (
                    jsonify({"message": "Invalid token format. Use: Bearer <token>"}),
                    401,
                )

            token = parts[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            customer_id = data["customer_id"]
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
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check if Authorization header exists
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]

            # Validate Authorization header format
            parts = auth_header.split()

            # Should have exactly 2 parts: "Bearer" and the token
            if len(parts) != 2:
                return (
                    jsonify({"message": "Invalid token format. Use: Bearer <token>"}),
                    401,
                )

            # Should start with "Bearer"
            if parts[0].lower() != "bearer":
                return (
                    jsonify({"message": "Invalid token format. Use: Bearer <token>"}),
                    401,
                )

            token = parts[1]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            # Check if token has mechanic role
            if data.get("role") != "mechanic":
                return (
                    jsonify({"message": "Unauthorized - Mechanic token required"}),
                    403,
                )

            mechanic_id = data["mechanic_id"]
        except ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except JWTError:
            return jsonify({"message": "Token is invalid"}), 401
        except Exception:
            return jsonify({"message": "Token is invalid"}), 401

        return f(mechanic_id, *args, **kwargs)

    return decorated
