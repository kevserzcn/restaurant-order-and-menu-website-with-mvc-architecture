"""
Payment Service
===============
Ödeme iş mantığı.

SOLID: Single Responsibility - Sadece ödeme business logic
SOLID: Open/Closed - Strategy pattern ile genişletilebilir
SOLID: Dependency Inversion - PaymentStrategy abstraction'ına bağımlı
"""

from typing import Optional
from datetime import datetime
from repositories import PaymentRepository, OrderRepository, TableRepository
from models.payment import Payment
from extensions import db
from .payment_strategies import PaymentContext

class PaymentService:
    """Ödeme servisi"""
    
    def __init__(self):
        self.payment_repo = PaymentRepository()
        self.order_repo = OrderRepository()
        self.table_repo = TableRepository()
        self.payment_context = PaymentContext()
    
    def process_payment(self, order_id: int, payment_method: str, **payment_data) -> Optional[Payment]:
        """Ödemeyi işle - Strategy pattern kullanarak"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return None
        
        # Zaten ödenmiş siparişler için tekrar ödeme yapılamaz
        if order.status == 'paid':
            return None
        
        # payment_data içinde amount varsa çıkar (çakışmayı önle)
        payment_data.pop('amount', None)
        
        # transaction_id varsa kullan, yoksa oluştur
        transaction_id = payment_data.pop('transaction_id', None)
        if not transaction_id:
            transaction_id = f'PAY_{order_id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        
        # Strategy pattern ile ödemeyi işle
        result = self.payment_context.process_payment(
            payment_method, 
            order.total_amount,
            **payment_data
        )
        
        if not result['success']:
            return None
        
        # Ödeme kaydı oluştur
        payment = Payment(
            order_id=order_id,
            amount=order.total_amount,
            payment_method=payment_method,
            status='completed',
            transaction_id=transaction_id
        )
        db.session.add(payment)
        
        # Sipariş durumunu güncelle
        order.status = 'paid'
        db.session.commit()
        
        # Masayı boşalt
        if order.table_id:
            self.table_repo.set_occupied(order.table_id, False)
        
        return payment
    
    def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Ödeme detayını getir"""
        return self.payment_repo.get_by_id(payment_id)
    
    def get_order_payments(self, order_id: int):
        """Siparişin ödemelerini getir"""
        return self.payment_repo.get_by_order(order_id)
    
    def get_today_revenue(self) -> float:
        """Bugünkü geliri hesapla"""
        payments = self.payment_repo.get_today_payments()
        return sum(p.amount for p in payments if p.status == 'completed')
    
    def get_monthly_revenue(self) -> float:
        """Aylık geliri hesapla"""
        payments = self.payment_repo.get_monthly_payments()
        return sum(p.amount for p in payments if p.status == 'completed')
    
    def get_total_revenue(self) -> float:
        """Toplam geliri hesapla"""
        return self.payment_repo.get_total_revenue()
    
    def get_revenue_by_method(self):
        """Ödeme yöntemine göre gelir"""
        return self.payment_repo.get_revenue_by_method()
