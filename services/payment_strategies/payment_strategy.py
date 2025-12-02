from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentStrategy(ABC):
    
    @abstractmethod
    def process(self, amount: float, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        pass
    
    @abstractmethod
    def validate(self, **kwargs) -> bool:
        pass


class CashPaymentStrategy(PaymentStrategy):
    
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
    
    def process(self, amount: float, **kwargs) -> Dict[str, Any]:
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
        return True


class PaymentContext:
    
    def __init__(self):
        self._strategies = {
            'cash': CashPaymentStrategy(),
            'card': CardPaymentStrategy()
        }
    
    def get_strategy(self, method: str) -> PaymentStrategy:
        strategy = self._strategies.get(method)
        if not strategy:
            raise ValueError(f"Geçersiz ödeme yöntemi: {method}")
        return strategy
    
    def process_payment(self, method: str, amount: float, **kwargs) -> Dict[str, Any]:
        strategy = self.get_strategy(method)
        
        if not strategy.validate(**kwargs):
            return {
                'success': False,
                'message': 'Ödeme bilgileri geçersiz'
            }
        
        return strategy.process(amount, **kwargs)
