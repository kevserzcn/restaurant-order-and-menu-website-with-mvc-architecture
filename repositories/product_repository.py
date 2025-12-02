from typing import List, Optional
from models.product import Product
from .base_repository import BaseRepository

class ProductRepository(BaseRepository[Product]):
    
    def __init__(self):
        super().__init__(Product)
    
    def get_available_products(self) -> List[Product]:
        return self.filter_by(is_available=True)
    
    def get_by_category(self, category: str) -> List[Product]:
        return self.model.query.filter_by(
            category=category,
            is_available=True
        ).all()
    
    def get_by_name(self, name: str) -> Optional[Product]:
        return self.first_by(name=name)
    
    def search(self, query: str) -> List[Product]:
        return self.model.query.filter(
            Product.name.ilike(f'%{query}%')
        ).all()
    
    def update_availability(self, product_id: int, is_available: bool) -> bool:
        product = self.get_by_id(product_id)
        if product:
            product.is_available = is_available
            self.save(product)
            return True
        return False
