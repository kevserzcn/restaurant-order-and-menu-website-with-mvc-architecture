from typing import List, Optional
from datetime import datetime
from repositories import OrderRepository, TableRepository
from models.order import Order, OrderItem
from config import db

class OrderService:
    
    def __init__(self):
        self.order_repo = OrderRepository()
        self.table_repo = TableRepository()
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.order_repo.get_by_id(order_id)
    
    def get_all_orders(self) -> List[Order]:
        return self.order_repo.get_all()
    
    def mark_order_as_paid(self, order_id: int) -> bool:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        order.status = 'paid'
        order.updated_at = datetime.utcnow()
        
        from models.payment import Payment
        existing_payment = Payment.query.filter_by(order_id=order_id).first()
        
        if not existing_payment:
            payment = Payment(
                order_id=order_id,
                amount=order.total_amount,
                payment_method='cash',
                status='completed'
            )
            db.session.add(payment)
        
        if order.table_id:
            other_active = Order.query.filter(
                Order.table_id == order.table_id,
                Order.id != order.id,
                Order.status.in_(['pending', 'completed', 'payment_pending'])
            ).count()
            
            if other_active == 0:
                self.table_repo.set_occupied(order.table_id, False)
        
        self.order_repo.save(order)
        return True
    
    def create_order(self, user_id: int, table_id: Optional[int] = None, items: Optional[List] = None) -> Order:
        order_data = {'user_id': user_id, 'status': 'pending'}
        if table_id:
            order_data['table_id'] = table_id
        order = self.order_repo.create(**order_data)
        
        if items:
            for item_data in items:
                self.add_item_to_order(
                    order_id=order.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
        
        return order
    
    def get_order(self, order_id: int) -> Optional[Order]:
        return self.order_repo.get_by_id(order_id)
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        return self.order_repo.get_by_user(user_id)
    
    def get_active_orders(self) -> List[Order]:
        return self.order_repo.get_by_statuses(['pending', 'completed', 'payment_pending'])
    
    def get_pending_orders(self) -> List[Order]:
        return self.order_repo.get_by_status('pending')
    
    def get_payment_pending_orders(self) -> List[Order]:
        from sqlalchemy import desc
        return Order.query.filter_by(
            status='payment_pending'
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).all()
    
    def add_item_to_order(self, order_id: int, product_id: int, quantity: int, price: float) -> OrderItem:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Sipariş bulunamadı: {order_id}")
        
        existing_item = OrderItem.query.filter_by(
            order_id=order_id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            db.session.commit()
            order.calculate_total()
            db.session.commit()
            return existing_item
        else:
            order_item = OrderItem(
                order_id=order_id,
                product_id=product_id,
                quantity=quantity,
                price=price
            )
            db.session.add(order_item)
            db.session.commit()
            order.calculate_total()
            db.session.commit()
            return order_item
    
    def remove_item_from_order(self, order_id: int, item_id: int) -> bool:
        from models import OrderItem
        item = OrderItem.query.get(item_id)
        if item and item.order_id == order_id:
            db.session.delete(item)
            db.session.commit()
            order = self.order_repo.get_by_id(order_id)
            if order:
                order.calculate_total()
                db.session.commit()
            return True
        return False
    
    def calculate_order_total(self, order_id: int) -> float:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return 0.0
        
        total = sum(item.quantity * item.price for item in order.items.all())
        order.total_amount = total
        self.order_repo.save(order)
        return total
    
    def update_order_status(self, order_id: int, new_status: str) -> bool:
        return self.order_repo.update_status(order_id, new_status)
    
    def place_order(self, order_id: int, table_id: int) -> bool:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        order.table_id = table_id
        order.status = 'pending'
        order.updated_at = datetime.utcnow()
        
        self.table_repo.set_occupied(table_id, True)
        
        self.calculate_order_total(order_id)
        
        self.order_repo.save(order)
        return True
    
    def cancel_order(self, order_id: int) -> bool:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        order.status = 'cancelled'
        
        if order.table_id:
            other_active = Order.query.filter(
                Order.table_id == order.table_id,
                Order.id != order.id,
                Order.status.in_(['pending', 'completed', 'payment_pending'])
            ).count()
            
            if other_active == 0:
                self.table_repo.set_occupied(order.table_id, False)
        
        self.order_repo.save(order)
        return True
    
    def request_payment(self, order_id: int) -> bool:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        if order.status not in ['pending', 'completed']:
            return False
        
        order.status = 'payment_pending'
        order.updated_at = datetime.utcnow()
        self.order_repo.save(order)
        
        db.session.refresh(order)
        return order.status == 'payment_pending'
