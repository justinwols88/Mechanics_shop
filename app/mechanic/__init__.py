from flask import Blueprint

mechanic_bp = Blueprint('mechanic', __name__)

from app.mechanic import routes