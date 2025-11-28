"""
Mechanics Routes
"""
from flask import Blueprint

mechanics_bp = Blueprint('mechanics', __name__)

@mechanics_bp.route('/mechanics', methods=['GET'])
def get_mechanics():
    """Get mechanics"""
    return {"message": "mechanics endpoint"}, 200
