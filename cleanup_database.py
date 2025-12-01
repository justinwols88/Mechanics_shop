#!/usr/bin/env python3
"""
Cleanup script to remove service tickets with NULL customer_id
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def cleanup_database():
    print("🧹 Cleaning up database...")
    
    try:
        from app import create_app, db
        from config import ProductionConfig
        from app.models.service_ticket import ServiceTicket
        
        app = create_app(ProductionConfig)
        
        with app.app_context():
            # Find and delete service tickets with NULL customer_id
            bad_tickets = ServiceTicket.query.filter(ServiceTicket.customer_id == None).all()
            
            if bad_tickets:
                print(f"❌ Found {len(bad_tickets)} service tickets with NULL customer_id")
                
                for ticket in bad_tickets:
                    print(f"🗑️  Deleting ticket ID {ticket.id}: {ticket.vehicle_info}")
                    db.session.delete(ticket)
                
                db.session.commit()
                print("✅ Cleanup completed successfully")
            else:
                print("✅ No problematic tickets found")
                
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    cleanup_database()