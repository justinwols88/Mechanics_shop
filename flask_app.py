# flask_app.py
from app import create_app, db
from config import ProductionConfig

app = create_app(ProductionConfig)

# Create tables when app starts
with app.app_context():
    db.create_all()
    print("✓ Database tables created successfully!")

if __name__ == '__main__':
    # Development server
    app.run(debug=True)