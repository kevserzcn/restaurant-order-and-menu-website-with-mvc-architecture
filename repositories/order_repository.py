from typing import List, Optional
from datetime import datetime, date
from models.order import Order
from sqlalchemy import desc, func
from config import db
from .base_repository import BaseRepository

class OrderRepository(BaseRepository[Order]):
    
    def __init__(self):
        super().__init__(Order)
    
    def get_by_status(self, status: str) -> List[Order]:
        return self.filter_by(status=status)
    
    def get_by_statuses(self, statuses: List[str]) -> List[Order]:
        return self.model.query.filter(
            Order.status.in_(statuses)
        ).all()
    
    def get_by_user(self, user_id: int) -> List[Order]:
        return self.model.query.filter_by(
            user_id=user_id
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).all()
    
    def get_latest_by_user(self, user_id: int, statuses: List[str]) -> Optional[Order]:
        return self.model.query.filter(
            Order.user_id == user_id,
            Order.status.in_(statuses)
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).first()
    
    def get_by_table(self, table_id: int) -> List[Order]:
        return self.filter_by(table_id=table_id)
    
    def get_current_by_table(self, table_id: int) -> Optional[Order]:
        return self.model.query.filter(
            Order.table_id == table_id,
            Order.status.in_(['pending', 'completed', 'payment_pending'])
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).first()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Order]:
        return self.model.query.filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).all()
    
    def get_today_orders(self) -> List[Order]:
        today = datetime.now().date()
        return self.get_by_date_range(today, today)
    
    def count_by_status(self, status: str) -> int:
        return self.model.query.filter_by(status=status).count()
    
    def update_status(self, order_id: int, new_status: str) -> bool:
        order = self.get_by_id(order_id)
        if order:
            order.status = new_status
            order.updated_at = datetime.utcnow()
            self.save(order)
            return True
        return False
