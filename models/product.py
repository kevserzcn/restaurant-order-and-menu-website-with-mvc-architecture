"""
Ürün Modeli
===========
Restoran menüsündeki ürünleri temsil eden veritabanı modeli.

Alanlar:
- id: Benzersiz ürün kimliği
- name: Ürün adı
- description: Ürün açıklaması
- price: Fiyat (TL)
- category: Kategori (yemek, tatlı, içecek, salata)
- image_url: Ürün resmi URL'i
- is_available: Menüde müsait mi?
- created_at: Eklenme tarihi

Metodlar:
- to_dict(): JSON serialization için dictionary'ye çevirme

Kullanım Alanları:
- Admin panelinde ürün yönetimi
- Müşteri menüsünde gösterim
- Sipariş oluşturma
- API endpoint'lerinde JSON response
"""

from extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # yemek, tatlı, içecek, salata
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    def __init__(self, name, description, price, category, image_url=None):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.image_url = image_url
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def get_image_url(self):
        """Resim URL'sini döndürür"""
        if not self.image_url:
            return None
        
        # Eğer HTTP ile başlıyorsa direkt döndür
        if self.image_url.startswith('http'):
            return self.image_url
        
        # Eğer static/images/ ile başlıyorsa direkt döndür
        if self.image_url.startswith('static/images/'):
            return self.image_url
        
        # Sadece dosya adı varsa static/images/ ekle
        return f"static/images/{self.image_url}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'is_available': self.is_available
        }
