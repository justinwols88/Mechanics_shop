from functools import wraps
from flask import request, jsonify, current_app
from jose import jwt


def encode_token(customer_id):
    payload = {"customer_id": customer_id}
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            customer_id = data['customer_id']
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
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            if data.get('role') != 'mechanic':
                return jsonify({"message": "Unauthorized"}), 403
            mechanic_id = data['mechanic_id']
        except Exception:
            return jsonify({"message": "Token is invalid"}), 401
        return f(mechanic_id, *args, **kwargs)
    return decorated