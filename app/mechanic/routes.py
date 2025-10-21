from flask import request, jsonify
from app.mechanic import mechanic_bp
from app.models import Mechanic
from app import db, limiter, cache
from app.mechanic.schemas import mechanic_schema, mechanics_schema

@mechanic_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting: 5 requests per minute
def create_mechanic():
    """
    RATE LIMITED: 5 requests per minute
    Why: Prevent spam creation of mechanic accounts and potential abuse.
    This is important because creating mechanics should be an admin function.
    """
    try:
        data = request.get_json()
        
        errors = mechanic_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        mechanic = mechanic_schema.load(data)
        db.session.add(mechanic)
        db.session.commit()
        
        # Clear the cache when new data is added
        cache.delete('all_mechanics')
        
        return mechanic_schema.jsonify(mechanic), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mechanic_bp.route('/', methods=['GET'])
@cache.cached(timeout=60, key_prefix='all_mechanics')  # Cache for 60 seconds
def get_mechanics():
    """
    CACHED: 60 seconds
    Why: This endpoint returns all mechanics which doesn't change frequently.
    Caching reduces database load and improves response time for frequently accessed data.
    """
    try:
        mechanics = Mechanic.query.all()
        return mechanics_schema.jsonify(mechanics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mechanic_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("10 per minute")  # Rate limiting: 10 requests per minute
def update_mechanic(id):
    """
    RATE LIMITED: 10 requests per minute
    Why: Prevent rapid, automated updates that could indicate abuse or bugs.
    This allows reasonable update frequency while preventing misuse.
    """
    try:
        mechanic = Mechanic.query.get_or_404(id)
        data = request.get_json()
        
        errors = mechanic_schema.validate(data, partial=True)
        if errors:
            return jsonify({"errors": errors}), 400
        
        mechanic = mechanic_schema.load(data, instance=mechanic, partial=True)
        db.session.commit()
        
        # Clear cache when data is updated
        cache.delete('all_mechanics')
        
        return mechanic_schema.jsonify(mechanic)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mechanic_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("3 per minute")  # Rate limiting: 3 requests per minute
def delete_mechanic(id):
    """
    RATE LIMITED: 3 requests per minute
    Why: Deleting mechanics is a sensitive operation that should be done carefully.
    This prevents mass deletion attacks or accidental rapid deletions.
    """
    try:
        mechanic = Mechanic.query.get_or_404(id)
        db.session.delete(mechanic)
        db.session.commit()
        
        # Clear cache when data is deleted
        cache.delete('all_mechanics')
        
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
