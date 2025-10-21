from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask import current_app

# Association table for many-to-many relationship
ticket_mechanics = db.Table('ticket_mechanics',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'), primary_key=True)
)

class Customer(db.Model):
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    service_tickets = db.relationship('ServiceTicket', back_populates='customer')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Mechanic(db.Model):
    __tablename__ = 'mechanic'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(100))
    
    service_tickets = db.relationship('ServiceTicket', secondary=ticket_mechanics, back_populates='mechanics')

class ServiceTicket(db.Model):
    __tablename__ = 'service_ticket'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(100), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    customer = db.relationship('Customer', back_populates='service_tickets')
    mechanics = db.relationship('Mechanic', secondary=ticket_mechanics, back_populates='service_tickets')

# Token encoding function
def encode_token(customer_id):
    """
    Creates a JWT token specific to a customer
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': customer_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_token(token):
    """
    Decodes the JWT token and returns customer_id
    """
    try:
        payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
