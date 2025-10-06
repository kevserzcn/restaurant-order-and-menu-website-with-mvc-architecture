from extensions import db
from datetime import datetime

class Table(db.Model):
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=4)
    is_occupied = db.Column(db.Boolean, default=False)
    waiter_name = db.Column(db.String(100))  # Garson girişi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='table', lazy='dynamic')
    
    def __init__(self, table_number, capacity=4, waiter_name=None):
        self.table_number = table_number
        self.capacity = capacity
        self.waiter_name = waiter_name
    
    def get_current_order(self):
        """Get the current active order for this table"""
        return self.orders.filter_by(status='pending').first()
    
    def get_total_amount(self):
        """Get total amount for current order"""
        current_order = self.get_current_order()
        if current_order:
            return current_order.calculate_total()
        return 0.0
    
    def to_dict(self):
        current_order = self.get_current_order()
        return {
            'id': self.id,
            'table_number': self.table_number,
            'capacity': self.capacity,
            'is_occupied': self.is_occupied,
            'waiter_name': self.waiter_name,
            'current_order': current_order.to_dict() if current_order else None,
            'total_amount': self.get_total_amount()
        }
