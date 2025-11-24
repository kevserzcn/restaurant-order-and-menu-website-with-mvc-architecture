"""
Payment Strategy Pattern
========================
Farklı ödeme yöntemleri için strategy pattern.

SOLID: Open/Closed Principle
- Yeni ödeme yöntemi eklemek için mevcut kodu değiştirmeyiz
- Sadece yeni strategy sınıfı ekleriz
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentStrategy(ABC):
    """Ödeme strategy interface"""
    
    @abstractmethod
    def process(self, amount: float, **kwargs) -> Dict[str, Any]:
        """Ödemeyi işle"""
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Ödeme yöntemi adı"""
        pass
    
    @abstractmethod
    def validate(self, **kwargs) -> bool:
        """Ödeme bilgilerini doğrula"""
        pass


class CashPaymentStrategy(PaymentStrategy):
    """Nakit ödeme stratejisi"""
    
    def process(self, amount: float, **kwargs) -> Dict[str, Any]:
        return {
            'success': True,
            'method': 'cash',
            'amount': amount,
            'message': 'Nakit ödeme alındı'
        }
    
    def get_method_name(self) -> str:
        return 'cash'
    
    def validate(self, **kwargs) -> bool:
        return True


class CardPaymentStrategy(PaymentStrategy):
    """Kart ödeme stratejisi"""
    
    def process(self, amount: float, **kwargs) -> Dict[str, Any]:
        # Gerçek uygulamada kart işleme API'si çağrılır
        card_number = kwargs.get('card_number', '')
        
        return {
            'success': True,
            'method': 'card',
            'amount': amount,
            'card_last_4': card_number[-4:] if card_number else 'XXXX',
            'message': 'Kart ödemesi başarılı'
        }
    
    def get_method_name(self) -> str:
        return 'card'
    
    def validate(self, **kwargs) -> bool:
        # Admin kasada kart ile ödeme alıyorsa kart numarası gerekmez
        # Gerçek uygulamada POS cihazı entegrasyonu yapılabilir
        return True


class PaymentContext:
    """Payment strategy context - ödeme yöntemini seçer"""
    
    def __init__(self):
        self._strategies = {
            'cash': CashPaymentStrategy(),
            'card': CardPaymentStrategy()
        }
    
    def get_strategy(self, method: str) -> PaymentStrategy:
        """Ödeme yöntemine göre strategy döndür"""
        strategy = self._strategies.get(method)
        if not strategy:
            raise ValueError(f"Geçersiz ödeme yöntemi: {method}")
        return strategy
    
    def process_payment(self, method: str, amount: float, **kwargs) -> Dict[str, Any]:
        """Ödemeyi işle"""
        strategy = self.get_strategy(method)
        
        if not strategy.validate(**kwargs):
            return {
                'success': False,
                'message': 'Ödeme bilgileri geçersiz'
            }
        
        return strategy.process(amount, **kwargs)
