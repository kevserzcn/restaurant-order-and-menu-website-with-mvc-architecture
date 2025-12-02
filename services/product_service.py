from typing import List, Optional
from repositories import ProductRepository
from models.product import Product

class ProductService:
    
    def __init__(self):
        self.product_repo = ProductRepository()
    
    def create_product(self, name: str, price: float, category: str, 
                      description: Optional[str] = None, 
                      image_url: Optional[str] = None) -> Product:
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
        return self.product_repo.get_by_id(product_id)
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.get_product(product_id)
    
    def get_all_products(self) -> List[Product]:
        return self.product_repo.get_all()
    
    def get_available_products(self) -> List[Product]:
        return self.product_repo.get_available_products()
    
    def get_products_by_category(self, category: str, available_only: bool = False) -> List[Product]:
        products = self.product_repo.get_by_category(category)
        if available_only:
            products = [p for p in products if p.is_available]
        return products
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return None
        
        if 'name' in kwargs:
            existing = self.product_repo.get_by_name(kwargs['name'])
            if existing and existing.id != product_id:
                raise ValueError(f"Bu ürün adı zaten mevcut: {kwargs['name']}")
        
        return self.product_repo.update(product, **kwargs)
    
    def delete_product(self, product_id: int) -> bool:
        try:
            from models.order import OrderItem
            order_items_count = OrderItem.query.filter_by(product_id=product_id).count()
            
            if order_items_count > 0:
                return self.product_repo.update_availability(product_id, False)
            else:
                product = self.product_repo.get_by_id(product_id)
                if not product:
                    return False
                return self.product_repo.delete(product)
        except Exception:
            return False
    
    def toggle_availability(self, product_id: int) -> bool:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
        
        new_availability = not product.is_available
        return self.product_repo.update_availability(product_id, new_availability)
    
    def search_products(self, query: str) -> List[Product]:
        return self.product_repo.search(query)
