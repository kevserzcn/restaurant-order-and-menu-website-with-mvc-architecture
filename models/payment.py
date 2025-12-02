from config import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  
    status = db.Column(db.String(20), default='pending')  
    transaction_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, order_id, amount, payment_method, transaction_id=None, status='pending'):
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.status = status
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat()
        }
