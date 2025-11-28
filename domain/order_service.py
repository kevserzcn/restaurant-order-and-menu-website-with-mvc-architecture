"""
Order Service
=============
Sipariş iş mantığı.

SOLID: Single Responsibility - Sadece sipariş business logic
"""

from typing import List, Optional
from datetime import datetime
from repositories import OrderRepository, TableRepository
from models.order import Order, OrderItem
from extensions import db

class OrderService:
    """Sipariş servisi"""
    
    def __init__(self):
        self.order_repo = OrderRepository()
        self.table_repo = TableRepository()
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Sipariş detayını getir"""
        return self.order_repo.get_by_id(order_id)
    
    def get_all_orders(self) -> List[Order]:
        """Tüm siparişleri getir"""
        return self.order_repo.get_all()
    
    def mark_order_as_paid(self, order_id: int) -> bool:
        """Siparişi ödendi olarak işaretle"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        order.status = 'paid'
        order.updated_at = datetime.utcnow()
        self.order_repo.save(order)
        return True
    
    def create_order(self, user_id: int, table_id: Optional[int] = None, items: Optional[List] = None) -> Order:
        """Yeni sipariş oluştur"""
        order_data = {'user_id': user_id, 'status': 'pending'}
        if table_id:
            order_data['table_id'] = table_id
        order = self.order_repo.create(**order_data)
        
        # Items varsa ekle (şimdilik kullanılmıyor, ileride lazım olabilir)
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
        """Sipariş detayını getir"""
        return self.order_repo.get_by_id(order_id)
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        """Kullanıcının siparişlerini getir"""
        return self.order_repo.get_by_user(user_id)
    
    def get_active_orders(self) -> List[Order]:
        """Aktif siparişleri getir"""
        return self.order_repo.get_by_statuses(['pending', 'completed', 'payment_pending'])
    
    def get_pending_orders(self) -> List[Order]:
        """Bekleyen siparişleri getir"""
        return self.order_repo.get_by_status('pending')
    
    def get_payment_pending_orders(self) -> List[Order]:
        """Ödeme bekleyen siparişleri getir (en yeni önce)"""
        from sqlalchemy import desc
        return Order.query.filter_by(
            status='payment_pending'
        ).order_by(
            desc(Order.updated_at),
            desc(Order.created_at),
            desc(Order.id)
        ).all()
    
    def add_item_to_order(self, order_id: int, product_id: int, quantity: int, price: float) -> OrderItem:
        """Siparişe ürün ekle"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Sipariş bulunamadı: {order_id}")
        
        # Aynı ürün var mı kontrol et
        existing_item = OrderItem.query.filter_by(
            order_id=order_id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
            db.session.commit()
            # Toplam tutarı güncelle
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
            # Toplam tutarı güncelle
            order.calculate_total()
            db.session.commit()
            return order_item
    
    def remove_item_from_order(self, order_id: int, item_id: int) -> bool:
        """Siparişten ürün çıkar"""
        from models import OrderItem
        item = OrderItem.query.get(item_id)
        if item and item.order_id == order_id:
            db.session.delete(item)
            db.session.commit()
            # Toplam tutarı güncelle
            order = self.order_repo.get_by_id(order_id)
            if order:
                order.calculate_total()
                db.session.commit()
            return True
        return False
    
    def calculate_order_total(self, order_id: int) -> float:
        """Sipariş toplamını hesapla"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return 0.0
        
        total = sum(item.quantity * item.price for item in order.items.all())
        order.total_amount = total
        self.order_repo.save(order)
        return total
    
    def update_order_status(self, order_id: int, new_status: str) -> bool:
        """Sipariş durumunu güncelle"""
        return self.order_repo.update_status(order_id, new_status)
    
    def place_order(self, order_id: int, table_id: int) -> bool:
        """Siparişi onayla"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        # Masa ata
        order.table_id = table_id
        order.status = 'pending'
        order.updated_at = datetime.utcnow()
        
        # Masa durumunu güncelle
        self.table_repo.set_occupied(table_id, True)
        
        # Toplamı hesapla
        self.calculate_order_total(order_id)
        
        self.order_repo.save(order)
        return True
    
    def cancel_order(self, order_id: int) -> bool:
        """Siparişi iptal et"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        order.status = 'cancelled'
        
        # Eğer masada başka aktif sipariş yoksa masayı boşalt
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
        """Ödeme talep et"""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        
        if order.status not in ['pending', 'completed']:
            return False
        
        order.status = 'payment_pending'
        order.updated_at = datetime.utcnow()
        self.order_repo.save(order)
        
        # Veritabanından tekrar okuyarak doğrula
        db.session.refresh(order)
        return order.status == 'payment_pending'
