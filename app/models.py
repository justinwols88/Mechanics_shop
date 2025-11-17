from .extensions import db

# Junction tables
service_mechanic = db.Table('service_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id')),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'))
)

ticket_inventory = db.Table('ticket_inventory',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id')),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'))
)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tickets = db.relationship('ServiceTicket', backref='customer', lazy=True)

class ServiceTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    mechanics = db.relationship('Mechanic', secondary=service_mechanic, backref='tickets')
    inventory = db.relationship('Inventory', secondary=ticket_inventory, backref='tickets')
    status = db.Column(db.String(50), nullable=False, default='open')

class Mechanic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
