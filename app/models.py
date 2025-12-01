from app.extensions import db

# Junction tables for many-to-many relationships
service_mechanic = db.Table('service_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id')),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'))
)

ticket_inventory = db.Table('ticket_inventory',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id')),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'))
)

