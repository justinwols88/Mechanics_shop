from app.extensions import db
from app.models import service_mechanic, ticket_inventory


# Junction tables
service_mechanic = db.Table(
    "service_mechanic",
    db.Column(
        "service_ticket_id",
        db.Integer,
        db.ForeignKey("service_ticket.id", name="fk_service_ticket_mechanic"),
    ),
    db.Column(
        "mechanic_id",
        db.Integer,
        db.ForeignKey("mechanic.id", name="fk_mechanic_service_ticket"),
    ),
)

ticket_inventory = db.Table(
    "ticket_inventory",
    db.Column(
        "service_ticket_id",
        db.Integer,
        db.ForeignKey("service_ticket.id", name="fk_service_ticket_inventory"),
    ),
    db.Column(
        "inventory_id",
        db.Integer,
        db.ForeignKey("inventory.id", name="fk_inventory_service_ticket"),
    ),
)


class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tickets = db.relationship("ServiceTicket", backref="customer", lazy=True)


class ServiceTicket(db.Model):
    __tablename__ = "service_ticket"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customer.id", name="fk_service_ticket_customer")
    )
    status = db.Column(db.String(50), nullable=False, default="open")

    mechanics = db.relationship(
        "Mechanic", secondary=service_mechanic, backref="service_tickets"
    )
    inventory = db.relationship(
        "Inventory", secondary=ticket_inventory, backref="service_tickets"
    )


class Mechanic(db.Model):
    __tablename__ = "mechanic"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(
        db.String(120), nullable=False
    )  # Changed from 'name' to 'part_name'
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )
