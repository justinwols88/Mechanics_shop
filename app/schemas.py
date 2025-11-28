from marshmallow import Schema, fields
from app.models import Customer, ServiceTicket, Mechanic, Inventory

# Simple manual schemas without SQLAlchemyAutoSchema

class CustomerSchema(Schema):
    id = fields.Int()
    email = fields.Str()
    password = fields.Str()

class ServiceTicketSchema(Schema):
    id = fields.Int()
    description = fields.Str()
    customer_id = fields.Int()
    status = fields.Str()

class MechanicSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    password = fields.Str()

class InventorySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    price = fields.Float()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class MechanicsSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
