"""
Migration script specifically for Render PostgreSQL database
"""
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from config import ProductionConfig
from sqlalchemy import text

def render_migration():
    print("🚀 Running Render database migration...")
    
    app = create_app(ProductionConfig)
    
    with app.app_context():
        try:
            connection = db.engine.connect()
            
            print("🔍 Checking current database schema...")
            
            # Get all tables in public schema
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            print("📋 Tables found:", tables)
            
            # Add missing columns to customer table
            if 'customer' in tables:
                print("\n👤 Checking customer table...")
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'customer' 
                    AND table_schema = 'public'
                """))
                customer_columns = [row[0] for row in result]
                print("Current customer columns:", customer_columns)
                
                # Add missing columns
                columns_to_add = [
                    ('first_name', 'VARCHAR(100)'),
                    ('last_name', 'VARCHAR(100)'),
                    ('phone', 'VARCHAR(20)'),
                    ('address', 'TEXT')
                ]
                
                for column_name, column_type in columns_to_add:
                    if column_name not in customer_columns:
                        print(f"➕ Adding {column_name} to customer table...")
                        connection.execute(text(f"ALTER TABLE customer ADD COLUMN {column_name} {column_type}"))
                        print(f"✅ Added {column_name}")
            
            # Add missing columns to mechanic table
            if 'mechanic' in tables:
                print("\n🔧 Checking mechanic table...")
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'mechanic' 
                    AND table_schema = 'public'
                """))
                mechanic_columns = [row[0] for row in result]
                print("Current mechanic columns:", mechanic_columns)
                
                # Add missing columns
                columns_to_add = [
                    ('first_name', 'VARCHAR(100)'),
                    ('last_name', 'VARCHAR(100)'),
                    ('specialization', 'VARCHAR(100)'),
                    ('years_experience', 'INTEGER DEFAULT 0'),
                    ('hourly_rate', 'FLOAT DEFAULT 0.0'),
                    ('is_active', 'BOOLEAN DEFAULT TRUE')
                ]
                
                for column_name, column_type in columns_to_add:
                    if column_name not in mechanic_columns:
                        print(f"➕ Adding {column_name} to mechanic table...")
                        connection.execute(text(f"ALTER TABLE mechanic ADD COLUMN {column_name} {column_type}"))
                        print(f"✅ Added {column_name}")
            
            connection.commit()
            connection.close()
            
            print("\n🎉 Render database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    render_migration()