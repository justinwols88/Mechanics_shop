"""
Mechanic Model - Fixed token generation
"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from config import Config

class Mechanic(db.Model):
    """Mechanic model for automotive shop mechanics"""

    __tablename__ = 'mechanic'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(100))
    years_experience = db.Column(db.Integer, default=0)
    hourly_rate = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        """Set hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Generate JWT token for authentication - FIXED"""
        try:
            payload = {
                'mechanic_id': self.id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
                'iat': datetime.datetime.now(datetime.timezone.utc),
                'type': 'mechanic'
            }
            return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        except Exception as e:
            # Fallback if timezone issues occur
            payload = {
                'mechanic_id': self.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'type': 'mechanic'
            }
            return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'specialization': self.specialization,
            'years_experience': self.years_experience,
            'hourly_rate': self.hourly_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Mechanic {self.email}>'