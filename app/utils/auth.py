"""
Authentication utilities for Mechanics Shop API
"""

# Added guarded import with fallback stubs
try:
    from flask import request, jsonify  # type: ignore
except ImportError:
    class _FallbackRequest:
        headers = {}
    request = _FallbackRequest()
    def jsonify(obj):
        return obj  # Fallback: install Flask for proper Response

import os
import importlib
try:
    from importlib.util import find_spec
except ImportError:
    find_spec = None
# Define placeholder exceptions for analyzers; real ones will override on import
class JWTError(Exception):
    pass
class ExpiredSignatureError(JWTError):
    pass
# Fixed jose imports: exceptions come from jose.exceptions; added type: ignore for optional dependency
try:
    from jose import jwt  # type: ignore
    from jose.exceptions import JWTError, ExpiredSignatureError  # type: ignore
except ImportError:
    spec = find_spec("jwt") if find_spec else None
    # Placeholders already defined; keep them unless overridden by PyJWT
    if spec:
        _pyjwt = importlib.import_module("jwt")
        jwt = _pyjwt  # PyJWT module
        try:
            from jwt.exceptions import ExpiredSignatureError as _PyJWTExpired  # type: ignore
            ExpiredSignatureError = _PyJWTExpired  # type: ignore
        except Exception:
            pass  # keep placeholder ExpiredSignatureError
    else:
        class _StubJWT:
            def encode(self, *_, **__):
                raise RuntimeError("Install python-jose or PyJWT for JWT support")
            def decode(self, *_, **__):
                raise RuntimeError("Install python-jose or PyJWT for JWT support")
        jwt = _StubJWT()

from datetime import datetime, timedelta
from functools import wraps

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
