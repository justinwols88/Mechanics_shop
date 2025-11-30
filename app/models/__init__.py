"""
Models package
"""
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket
from app.models.inventory import Inventory

__all__ = ['Customer', 'Mechanic', 'ServiceTicket', 'Inventory']