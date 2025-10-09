from extensions import db
from datetime import datetime
from .order import Order

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
        """Aktif (ödenmemiş) siparişi getir"""
        return (Order.query
                .filter(Order.table_id == self.id,
                        Order.status.in_(['pending', 'completed', 'payment_pending']))
                .order_by(Order.updated_at.desc(),
                          Order.created_at.desc(),
                          Order.id.desc())
                .first())
    
    def get_unpaid_order(self):
        """Ödenmemiş son siparişi getir"""
        return self.get_current_order()
    
    def get_total_amount(self):
        """Masadaki ödenmemiş siparişin toplam tutarı"""
        current_order = self.get_current_order()
        if current_order:
            if current_order.total_amount == 0 and current_order.items.count() > 0:
                current_order.calculate_total()
            return current_order.total_amount
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
