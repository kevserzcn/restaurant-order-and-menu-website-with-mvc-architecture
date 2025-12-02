from typing import Optional
from datetime import datetime
from repositories import PaymentRepository, OrderRepository, TableRepository
from models.payment import Payment
from config import db
from .payment_strategies import PaymentContext

class PaymentService:
    
    def __init__(self):
        self.payment_repo = PaymentRepository()
        self.order_repo = OrderRepository()
        self.table_repo = TableRepository()
        self.payment_context = PaymentContext()
    
    def process_payment(self, order_id: int, payment_method: str, **payment_data) -> Optional[Payment]:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return None
        
        if order.status == 'paid':
            return None
        
        payment_data.pop('amount', None)
        
        transaction_id = payment_data.pop('transaction_id', None)
        if not transaction_id:
            transaction_id = f'PAY_{order_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        result = self.payment_context.process_payment(
            payment_method, 
            order.total_amount,
            **payment_data
        )
        
        if not result['success']:
            return None
        
        payment = Payment(
            order_id=order_id,
            amount=order.total_amount,
            payment_method=payment_method,
            status='completed',
            transaction_id=transaction_id
        )
        db.session.add(payment)
        
        order.status = 'paid'
        db.session.commit()
        
        if order.table_id:
            self.table_repo.set_occupied(order.table_id, False)
        
        return payment
    
    def get_payment(self, payment_id: int) -> Optional[Payment]:
        return self.payment_repo.get_by_id(payment_id)
    
    def get_order_payments(self, order_id: int):
        return self.payment_repo.get_by_order(order_id)
