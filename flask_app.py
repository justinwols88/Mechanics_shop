# wsgi.py (for production)
import os
from app import create_app, db
from config import ProductionConfig

app = create_app(ProductionConfig)

# Create tables when the app starts in production
with app.app_context():
    db.create_all()
    print("✓ Production database tables created successfully!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)