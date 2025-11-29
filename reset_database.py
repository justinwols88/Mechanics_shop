# Create reset_database.py
from app import create_app, db
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from app.models.service_ticket import ServiceTicket

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create all tables with current schema
    db.create_all()
    
    print("✅ Database reset successfully!")