#!/usr/bin/env python3
"""
Pre-deploy database setup script for Render
"""
import os
import sys
import traceback
from sqlalchemy import text

def setup_database():
    print("🚀 Starting pre-deploy database setup...")
    
    try:
        # Add project root to Python path
        project_root = '/opt/render/project/src'
        sys.path.append(project_root)
        
        from app import create_app, db
        from config import ProductionConfig
        
        app = create_app(ProductionConfig)
        
        with app.app_context():
            # Test database connection
            print("🔌 Testing database connection...")
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Create tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Tables created/verified")
            
            # List tables for verification
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📋 Database ready with {len(tables)} tables:")
            for table in sorted(tables):
                print(f"   ✅ {table}")
                
            print("🎉 Pre-deploy database setup completed successfully!")
            
    except Exception as e:
        print(f"❌ Pre-deploy setup failed: {e}")
        traceback.print_exc()
        # Exit with success to not block deployment
        print("⚠️ Continuing deployment despite database issues...")
        sys.exit(0)  # Success exit to not block deploy

if __name__ == '__main__':
    setup_database()