from config import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], lazy='joined', overlaps="customer,orders")
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy='dynamic')
    
    def __init__(self, user_id, table_id=None, status='pending'):
        self.user_id = user_id
        self.table_id = table_id
        self.status = status
    
    def calculate_total(self):
        total = sum(item.quantity * item.product.price for item in self.items.all())
        self.total_amount = total
        return total
    
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def unique_items(self):
        return self.items.count()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'table_id': self.table_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items.all()]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, order_id, product_id, quantity, price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': self.price,
            'total': self.quantity * self.price
        }

