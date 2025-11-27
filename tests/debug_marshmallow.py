import sys
import os
sys.path.insert(0, '.')

print("=== Debugging Marshmallow ===")

try:
    from app.extensions import ma
    print(f"1. ma type: {type(ma)}")
    print(f"2. ma value: {ma}")
    
    # Check if SQLAlchemyAutoSchema exists
    if hasattr(ma, 'SQLAlchemyAutoSchema'):
        print(f"3. ma.SQLAlchemyAutoSchema: {ma.SQLAlchemyAutoSchema}")
        print(f"4. ma.SQLAlchemyAutoSchema type: {type(ma.SQLAlchemyAutoSchema)}")
    else:
        print("3. ma.SQLAlchemyAutoSchema does not exist")
        
    # Check marshmallow_sqlalchemy directly
    try:
        from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
        print(f"5. Direct SQLAlchemyAutoSchema: {SQLAlchemyAutoSchema}")
        print(f"6. Direct SQLAlchemyAutoSchema type: {type(SQLAlchemyAutoSchema)}")
    except ImportError as e:
        print(f"5. marshmallow_sqlalchemy not installed: {e}")
        
    # Check Flask-Marshmallow version
    try:
        import flask_marshmallow
        ver = getattr(flask_marshmallow, "__version__", None)
        if not ver:
            try:
                from importlib.metadata import version as _pkg_version
                ver = _pkg_version("flask-marshmallow")
            except Exception:
                ver = None
        if ver:
            print(f"7. Flask-Marshmallow version: {ver}")
        else:
            print("7. Could not get Flask-Marshmallow version")
    except:
        print("7. Could not get Flask-Marshmallow version")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()