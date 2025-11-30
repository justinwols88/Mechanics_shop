"""
Database reset script with proper error handling
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import Inventory
from app.models.service_ticket import ServiceTicket

def reset_database():
    """Reset database with sample data"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Resetting database...")
            
            # Drop all tables
            db.drop_all()
            print("✅ Tables dropped")
            
            # Create all tables with current schema
            db.create_all()
            print("✅ Tables created")
            
            # Create sample data
            print("📝 Creating sample data...")
            
            # Sample customer
            customer = Customer(
                first_name="John",
                last_name="Doe",
                email="customer@example.com",
                phone="+1234567890",
                address="123 Main St, City, State"
            )
            customer.set_password("password123")
            db.session.add(customer)
            
            # Sample mechanic
            mechanic = Mechanic(
                first_name="Jane",
                last_name="Smith", 
                email="mechanic@example.com",
                specialization="Brake Systems",
                years_experience=5,
                hourly_rate=45.0
            )
            mechanic.set_password("mechanic123")
            db.session.add(mechanic)
            
            # Sample inventory
            inventory = Inventory(
                part_name="Brake Pads - Premium",
                part_number="BP-PREM-001",
                description="Premium ceramic brake pads",
                quantity=25,
                price=49.99,
                category="Brakes",
                supplier="AutoParts Inc"
            )
            db.session.add(inventory)
            
            # Sample service ticket
            ticket = ServiceTicket(
                customer_id=1,
                vehicle_info="Toyota Camry 2020 - VIN: 123456789",
                issue_description="Brakes making grinding noise",
                status="open",
                priority="high",
                estimated_hours=2.5
            )
            db.session.add(ticket)
            
            db.session.commit()
            print("✅ Sample data created")
            print("🎉 Database reset successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error resetting database: {e}")
            sys.exit(1)

if __name__ == '__main__':
    reset_database()