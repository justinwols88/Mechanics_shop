"""
Customer Model - Fixed token generation
"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from config import Config

class Customer(db.Model):
    """Customer model for automotive shop customers"""

    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
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
                'customer_id': self.id,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
                'iat': datetime.datetime.now(datetime.timezone.utc),
                'type': 'customer'
            }
            return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        except Exception:
            # Fallback if timezone issues occur
            payload = {
                'customer_id': self.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'type': 'customer'
            }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Customer {self.email}>'