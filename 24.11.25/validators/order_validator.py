"""
Order Validator
===============
Sipariş business validation.

SOLID: Single Responsibility - Sadece sipariş validasyonu
"""

from typing import Optional

class OrderValidator:
    """Sipariş validator"""
    
    @staticmethod
    def validate_quantity(quantity: int) -> tuple[bool, Optional[str]]:
        """Miktar validasyonu"""
        if quantity <= 0:
            return False, "Miktar 0'dan büyük olmalıdır"
        if quantity > 100:
            return False, "Tek seferde en fazla 100 adet sipariş verilebilir"
        return True, None
    
    @staticmethod
    def validate_order_status(current_status: str, new_status: str) -> tuple[bool, Optional[str]]:
        """Sipariş durum geçişi validasyonu"""
        # Geçerli durum geçişleri
        valid_transitions = {
            'pending': ['completed', 'cancelled'],
            'completed': ['payment_pending', 'cancelled'],
            'payment_pending': ['paid', 'cancelled'],
            'paid': [],  # Ödenen sipariş değiştirilemez
            'cancelled': []  # İptal edilen sipariş değiştirilemez
        }
        
        if current_status not in valid_transitions:
            return False, f"Geçersiz sipariş durumu: {current_status}"
        
        if new_status not in valid_transitions[current_status]:
            return False, f"'{current_status}' durumundan '{new_status}' durumuna geçiş yapılamaz"
        
        return True, None
    
    @staticmethod
    def can_cancel_order(status: str) -> tuple[bool, Optional[str]]:
        """Sipariş iptal edilebilir mi"""
        if status in ['paid']:
            return False, "Ödenen sipariş iptal edilemez"
        if status == 'cancelled':
            return False, "Sipariş zaten iptal edilmiş"
        return True, None
    
    @staticmethod
    def can_add_items(status: str) -> tuple[bool, Optional[str]]:
        """Siparişe ürün eklenebilir mi"""
        if status in ['paid', 'cancelled']:
            return False, f"'{status}' durumundaki siparişe ürün eklenemez"
        return True, None
