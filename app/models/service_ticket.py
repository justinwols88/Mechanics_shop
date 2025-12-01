"""
Service Ticket Model with Fixed Relationships
"""
"""Service Ticket Model with Fixed Relationships"""
from app import db
from collections.abc import Iterable

class ServiceTicket(db.Model):
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
    mechanics = db.relationship('Mechanic', secondary='service_mechanic', backref='service_tickets', lazy='select')
    inventory = db.relationship('Inventory', secondary='ticket_inventory', backref='service_tickets', lazy='select')

    def to_dict(self):
        # Handle relationships that may be dynamic (query) or list-like
        # Safely resolve relationship collections that may sometimes appear as RelationshipProperty
        mech_attr = getattr(self, 'mechanics', [])
        inv_attr = getattr(self, 'inventory', [])

        # Normalize relationship collections to concrete lists without unsafe attribute checks
        try:
            from sqlalchemy.orm.query import Query  # SQLAlchemy Query (for lazy='dynamic')
        except Exception:
            Query = tuple()  # Fallback to avoid import issues

        def to_list(attr):
            # If it's a SQLAlchemy Query, fetch results with .all()
            if 'Query' in str(type(attr)) or (Query and isinstance(attr, Query)):
                return attr.all()
            # If it's already iterable (e.g., list, InstrumentedList), cast to list
            return list(attr) if isinstance(attr, Iterable) else []

        mechanics_list = to_list(mech_attr)
        inventory_list = to_list(inv_attr)

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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'mechanics': [m.to_dict() for m in mechanics_list] if mechanics_list else [],
            'inventory': [i.to_dict() for i in inventory_list] if inventory_list else []
        }