"""
Payment Repository
==================
Ödeme veritabanı işlemleri.

SOLID: Single Responsibility - Sadece Payment CRUD
"""

from typing import List
from datetime import datetime, date
from models.payment import Payment
from sqlalchemy import func
from extensions import db
from .base_repository import BaseRepository

class PaymentRepository(BaseRepository[Payment]):
    """Ödeme repository"""
    
    def __init__(self):
        super().__init__(Payment)
    
    def get_by_order(self, order_id: int) -> List[Payment]:
        """Siparişe göre ödemeleri getir"""
        return self.filter_by(order_id=order_id)
    
    def get_by_status(self, status: str) -> List[Payment]:
        """Duruma göre ödemeleri getir"""
        return self.filter_by(status=status)
    
    def get_completed_payments(self) -> List[Payment]:
        """Tamamlanmış ödemeleri getir"""
        return self.get_by_status('completed')
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Tarih aralığına göre ödemeleri getir"""
        return self.model.query.filter(
            func.date(Payment.created_at) >= start_date,
            func.date(Payment.created_at) <= end_date
        ).all()
    
    def get_today_payments(self) -> List[Payment]:
        """Bugünkü ödemeleri getir"""
        today = datetime.now().date()
        return self.model.query.filter(
            func.date(Payment.created_at) == today
        ).all()
    
    def get_monthly_payments(self) -> List[Payment]:
        """Bu ayki ödemeleri getir"""
        month_start = datetime.now().replace(day=1).date()
        return self.model.query.filter(
            func.date(Payment.created_at) >= month_start
        ).all()
    
    def get_total_revenue(self) -> float:
        """Toplam geliri hesapla"""
        result = db.session.query(
            func.sum(Payment.amount)
        ).filter_by(status='completed').scalar()
        return result or 0.0
    
    def get_revenue_by_method(self):
        """Ödeme yöntemine göre gelir"""
        return db.session.query(
            Payment.payment_method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total')
        ).filter_by(status='completed').group_by(Payment.payment_method).all()
