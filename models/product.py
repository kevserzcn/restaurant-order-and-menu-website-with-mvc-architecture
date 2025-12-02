from config import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False) 
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    def __init__(self, name, description, price, category, image_url=None):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.image_url = image_url
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def get_image_url(self):
        if not self.image_url:
            return None
        
        if self.image_url.startswith('http'):
            return self.image_url
        
        if self.image_url.startswith('static/images/'):
            return self.image_url
        
        return f"static/images/{self.image_url}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available
        }
