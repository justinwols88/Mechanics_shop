"""
Service Ticket Model with Fixed Relationships
"""
from app import db

class ServiceTicket(db.Model):
    """Service Ticket model for tracking repair jobs"""

    __tablename__ = 'service_ticket'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    vehicle_info = db.Column(db.String(200), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')
    priority = db.Column(db.String(20), default='medium')
    estimated_hours = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(),
                          onupdate=db.func.current_timestamp())

    # Fixed relationships
    customer = db.relationship('Customer', backref=db.backref('service_tickets', lazy=True))

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'vehicle_info': self.vehicle_info,
            'issue_description': self.issue_description,
            'status': self.status,
            'priority': self.priority,
            'estimated_hours': self.estimated_hours,
            'total_cost': self.total_cost,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<ServiceTicket {self.id}>'