from flask import request, jsonify
from app.mechanic import mechanic_bp
from app.models import Mechanic
from app import db
from app.mechanic.schemas import mechanic_schema, mechanics_schema

@mechanic_bp.route('/', methods=['POST'])
def create_mechanic():
    data = request.get_json()
    
    errors = mechanic_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    
    mechanic = mechanic_schema.load(data)
    db.session.add(mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(mechanic), 201

@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics)

@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    data = request.get_json()
    
    errors = mechanic_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400
    
    mechanic = mechanic_schema.load(data, instance=mechanic, partial=True)
    db.session.commit()
    
    return mechanic_schema.jsonify(mechanic)

@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    
    return '', 204