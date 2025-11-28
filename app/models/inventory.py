"""
Inventory Model
"""
from app import db

class Inventory(db.Model):
    """Inventory model for automotive parts"""
    
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(db.String(200), nullable=False)
    part_number = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(100))
    supplier = db.Column(db.String(200))
    min_stock_level = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'part_name': self.part_name,
            'part_number': self.part_number,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'supplier': self.supplier,
            'min_stock_level': self.min_stock_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Inventory {self.part_name}>'
