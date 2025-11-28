"""
Product Service
===============
Ürün iş mantığı.

SOLID: Single Responsibility - Sadece ürün business logic
"""

from typing import List, Optional
from repositories import ProductRepository
from models.product import Product

class ProductService:
    """Ürün servisi"""
    
    def __init__(self):
        self.product_repo = ProductRepository()
    
    def create_product(self, name: str, price: float, category: str, 
                      description: Optional[str] = None, 
                      image_url: Optional[str] = None) -> Product:
        """Yeni ürün oluştur"""
        # İsim kontrolü
        if self.product_repo.get_by_name(name):
            raise ValueError(f"Bu ürün adı zaten mevcut: {name}")
        
        return self.product_repo.create(
            name=name,
            price=price,
            category=category,
            description=description,
            image_url=image_url
        )
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Ürün detayını getir"""
        return self.product_repo.get_by_id(product_id)
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Ürün detayını getir (alias)"""
        return self.get_product(product_id)
    
    def get_all_products(self) -> List[Product]:
        """Tüm ürünleri getir"""
        return self.product_repo.get_all()
    
    def get_available_products(self) -> List[Product]:
        """Mevcut ürünleri getir"""
        return self.product_repo.get_available_products()
    
    def get_products_by_category(self, category: str, available_only: bool = False) -> List[Product]:
        """Kategoriye göre ürünleri getir"""
        products = self.product_repo.get_by_category(category)
        if available_only:
            products = [p for p in products if p.is_available]
        return products
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """Ürün bilgilerini güncelle"""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return None
        
        # İsim değişiyorsa kontrol et
        if 'name' in kwargs:
            existing = self.product_repo.get_by_name(kwargs['name'])
            if existing and existing.id != product_id:
                raise ValueError(f"Bu ürün adı zaten mevcut: {kwargs['name']}")
        
        return self.product_repo.update(product, **kwargs)
    
    def delete_product(self, product_id: int) -> bool:
        """Ürünü sil"""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
        
        return self.product_repo.delete(product)
    
    def toggle_availability(self, product_id: int) -> bool:
        """Ürün müsaitliğini değiştir"""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
        
        new_availability = not product.is_available
        return self.product_repo.update_availability(product_id, new_availability)
    
    def search_products(self, query: str) -> List[Product]:
        """Ürün ara"""
        return self.product_repo.search(query)
