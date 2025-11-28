"""
Order Repository
================
Sipariş veritabanı işlemleri.

SOLID: Single Responsibility - Sadece Order CRUD
"""

from typing import List, Optional
from datetime import datetime, date
from models.order import Order
from sqlalchemy import desc, func
from extensions import db
from .base_repository import BaseRepository

class OrderRepository(BaseRepository[Order]):
    """Sipariş repository"""
    
    def __init__(self):
        super().__init__(Order)
    
    def get_by_status(self, status: str) -> List[Order]:
        """Duruma göre siparişleri getir"""
        return self.filter_by(status=status)
    
    def get_by_statuses(self, statuses: List[str]) -> List[Order]:
        """Birden fazla duruma göre siparişleri getir"""
        return self.model.query.filter(
            Order.status.in_(statuses)
        ).all()
    
    def get_by_user(self, user_id: int) -> List[Order]:
        """Kullanıcıya göre siparişleri getir"""
        return self.model.query.filter_by(
            user_id=user_id
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).all()
    
    def get_latest_by_user(self, user_id: int, statuses: List[str]) -> Optional[Order]:
        """Kullanıcının en son siparişini getir"""
        return self.model.query.filter(
            Order.user_id == user_id,
            Order.status.in_(statuses)
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).first()
    
    def get_by_table(self, table_id: int) -> List[Order]:
        """Masaya göre siparişleri getir"""
        return self.filter_by(table_id=table_id)
    
    def get_current_by_table(self, table_id: int) -> Optional[Order]:
        """Masanın aktif siparişini getir"""
        return self.model.query.filter(
            Order.table_id == table_id,
            Order.status.in_(['pending', 'completed', 'payment_pending'])
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).first()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Order]:
        """Tarih aralığına göre siparişleri getir"""
        return self.model.query.filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).all()
    
    def get_today_orders(self) -> List[Order]:
        """Bugünkü siparişleri getir"""
        today = datetime.now().date()
        return self.get_by_date_range(today, today)
    
    def count_by_status(self, status: str) -> int:
        """Duruma göre sipariş sayısını say"""
        return self.model.query.filter_by(status=status).count()
    
    def update_status(self, order_id: int, new_status: str) -> bool:
        """Sipariş durumunu güncelle"""
        order = self.get_by_id(order_id)
        if order:
            order.status = new_status
            order.updated_at = datetime.utcnow()
            self.save(order)
            return True
        return False
