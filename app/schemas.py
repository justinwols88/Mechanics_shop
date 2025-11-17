from marshmallow import fields
from app.extensions import ma
from app.models import Customer, ServiceTicket, Mechanic, Inventory

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:  # type: ignore
        model = Customer
        include_relationships = True
        load_instance = True

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:  # type: ignore
        model = ServiceTicket
        include_relationships = True
        load_instance = True

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:  # type: ignore
        model = Mechanic
        include_relationships = True
        load_instance = True

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:  # type: ignore
        model = Inventory
        include_relationships = True
        load_instance = True

# Login schema
class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

# Mechanics list schema
class MechanicsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:  # type: ignore
        model = Mechanic
        include_relationships = True
        load_instance = True
