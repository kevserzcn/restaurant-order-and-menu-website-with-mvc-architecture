from typing import List, Optional

class ProductValidator:
    
    @staticmethod
    def validate_price(price: float) -> tuple[bool, Optional[str]]:
        if price <= 0:
            return False, "Fiyat 0'dan büyük olmalıdır"
        if price > 10000:
            return False, "Fiyat 10.000 TL'den küçük olmalıdır"
        return True, None
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, Optional[str]]:
        if not name or len(name.strip()) == 0:
            return False, "Ürün adı boş olamaz"
        if len(name) < 2:
            return False, "Ürün adı en az 2 karakter olmalıdır"
        if len(name) > 100:
            return False, "Ürün adı en fazla 100 karakter olmalıdır"
        return True, None
    
    @staticmethod
    def validate_category(category: str) -> tuple[bool, Optional[str]]:
        valid_categories = ['yemek', 'tatlı', 'içecek', 'salata']
        if category not in valid_categories:
            return False, f"Kategori {', '.join(valid_categories)} değerlerinden biri olmalıdır"
        return True, None
    
    @classmethod
    def validate_product(cls, name: str, price: float, category: str) -> tuple[bool, List[str]]:
        errors = []
        
        is_valid, error = cls.validate_name(name)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = cls.validate_price(price)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = cls.validate_category(category)
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors
