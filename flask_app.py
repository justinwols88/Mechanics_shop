# flask_app.py
from app import create_app, db
from config import ProductionConfig

app = create_app(ProductionConfig)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        app.run(debug=True)