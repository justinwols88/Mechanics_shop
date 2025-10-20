from app import db

class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(100))
    
    service_tickets = db.relationship('ServiceTicket', secondary='ticket_mechanics', back_populates='mechanics')

class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(100), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    mechanics = db.relationship('Mechanic', secondary='ticket_mechanics', back_populates='service_tickets')

ticket_mechanics = db.Table('ticket_mechanics',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'), primary_key=True)
)