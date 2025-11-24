"""
Payment Validator
=================
Ödeme business validation.

SOLID: Single Responsibility - Sadece ödeme validasyonu
"""

from typing import Optional

class PaymentValidator:
    """Ödeme validator"""
    
    @staticmethod
    def validate_amount(amount: float) -> tuple[bool, Optional[str]]:
        """Tutar validasyonu"""
        if amount <= 0:
            return False, "Ödeme tutarı 0'dan büyük olmalıdır"
        if amount > 50000:
            return False, "Tek seferde en fazla 50.000 TL ödeme yapılabilir"
        return True, None
    
    @staticmethod
    def validate_payment_method(method: str) -> tuple[bool, Optional[str]]:
        """Ödeme yöntemi validasyonu"""
        valid_methods = ['cash', 'card']
        if method not in valid_methods:
            return False, f"Ödeme yöntemi {', '.join(valid_methods)} değerlerinden biri olmalıdır"
        return True, None
    
    @staticmethod
    def can_process_payment(order_status: str) -> tuple[bool, Optional[str]]:
        """Ödeme işlenebilir mi"""
        if order_status == 'paid':
            return False, "Sipariş zaten ödenmiş"
        if order_status == 'cancelled':
            return False, "İptal edilen sipariş için ödeme yapılamaz"
        if order_status not in ['pending', 'completed', 'payment_pending']:
            return False, f"'{order_status}' durumundaki sipariş için ödeme yapılamaz"
        return True, None
    
    @staticmethod
    def validate_card_number(card_number: str) -> tuple[bool, Optional[str]]:
        """Kart numarası validasyonu (basit)"""
        # Gerçek uygulamada Luhn algoritması kullanılır
        card_number = card_number.replace(' ', '').replace('-', '')
        
        if not card_number.isdigit():
            return False, "Kart numarası sadece rakamlardan oluşmalıdır"
        
        if len(card_number) < 13 or len(card_number) > 19:
            return False, "Kart numarası 13-19 haneli olmalıdır"
        
        return True, None
    
    @staticmethod
    def validate_phone_number(phone: str) -> tuple[bool, Optional[str]]:
        """Telefon numarası validasyonu"""
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if not phone.isdigit():
            return False, "Telefon numarası sadece rakamlardan oluşmalıdır"
        
        if len(phone) < 10 or len(phone) > 11:
            return False, "Telefon numarası 10-11 haneli olmalıdır"
        
        return True, None
