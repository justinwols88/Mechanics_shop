"""Authentication utilities for Mechanics Shop API"""
import os
from datetime import datetime, timedelta
from functools import wraps

try:
    from flask import request, jsonify
except ImportError:
    class _FallbackRequest:
        headers = {}
    request = _FallbackRequest()
    def jsonify(obj):  # type: ignore
        return obj

# Unified JWT import logic (avoid duplicate ExpiredSignatureError declarations)
try:
    from jose import jwt  # type: ignore
    from jose.exceptions import JWTError, ExpiredSignatureError  # type: ignore
except ImportError:  # python-jose not available
    try:
        import jwt  # PyJWT
        from jwt.exceptions import ExpiredSignatureError  # type: ignore
        from jwt.exceptions import InvalidTokenError as JWTError  # type: ignore
    except ImportError:
        class ExpiredSignatureError(Exception):  # Fallback placeholder
            pass
        class JWTError(Exception):  # Fallback placeholder
            pass
        class _StubJWT:
            def encode(self, *_, **__):  # pragma: no cover
                raise RuntimeError("Install python-jose or PyJWT for JWT support")
            def decode(self, *_, **__):  # pragma: no cover
                raise RuntimeError("Install python-jose or PyJWT for JWT support")
        jwt = _StubJWT()  # type: ignore

# Use environment variable with fallback for CI/CD
SECRET_KEY = os.environ.get("SECRET_KEY") or "super secret secrets"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def encode_token(customer_id):
    # Added exp claim so expiration handling works
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"customer_id": customer_id, "exp": exp}
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
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"mechanic_id": mechanic_id, "role": "mechanic", "exp": exp}
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
