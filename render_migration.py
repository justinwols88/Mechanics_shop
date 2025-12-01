#!/usr/bin/env python3
"""
Migration script for Render PostgreSQL database
"""
import os
import sys
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    print("🚀 Starting Render database migration...")
    
    try:
        from app import create_app, db
        from config import ProductionConfig
        
        app = create_app(ProductionConfig)
        
        with app.app_context():
            # Test connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Verify tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📋 Found {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   ✅ {table}")
                
            print("🎉 Database migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    migrate_database()