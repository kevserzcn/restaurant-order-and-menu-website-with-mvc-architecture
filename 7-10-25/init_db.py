#!/usr/bin/env python3
"""
Database initialization script for Restaurant Menu System
"""

from app import create_app
from extensions import db
from models import Admin, Product
from werkzeug.security import generate_password_hash


def init_database():
    """Initialize database with default admin and sample products"""
    app = create_app()

    with app.app_context():
        # Tabloları oluştur
        db.create_all()

        # Varsayılan admin oluştur (yoksa)
        if not Admin.query.filter_by(email='admin@restaurant.com').first():
            admin = Admin(
                email='admin@restaurant.com',
                password=generate_password_hash('admin123'),
                name='Admin'
            )
            db.session.add(admin)
            print("✓ Default admin created")

        # Örnek ürünler
        sample_products = [
            # Yemekler
            {'name': 'Adana Kebap', 'description': 'Acılı kıyma ile hazırlanan geleneksel kebap', 'price': 45.00, 'category': 'yemek'},
            {'name': 'Urfa Kebap', 'description': 'Acısız kıyma ile hazırlanan kebap', 'price': 45.00, 'category': 'yemek'},
            {'name': 'Tavuk Şiş', 'description': 'Marine edilmiş tavuk göğsü', 'price': 35.00, 'category': 'yemek'},
            {'name': 'Kuzu Pirzola', 'description': 'Izgara kuzu pirzola', 'price': 55.00, 'category': 'yemek'},
            {'name': 'Balık Tava', 'description': 'Günlük taze balık', 'price': 40.00, 'category': 'yemek'},

            # Tatlılar
            {'name': 'Baklava', 'description': 'Geleneksel baklava', 'price': 25.00, 'category': 'tatlı'},
            {'name': 'Künefe', 'description': 'Sıcak künefe', 'price': 20.00, 'category': 'tatlı'},
            {'name': 'Sütlaç', 'description': 'Ev yapımı sütlaç', 'price': 15.00, 'category': 'tatlı'},
            {'name': 'Kazandibi', 'description': 'Geleneksel kazandibi', 'price': 18.00, 'category': 'tatlı'},

            # İçecekler
            {'name': 'Ayran', 'description': 'Ev yapımı ayran', 'price': 8.00, 'category': 'içecek'},
            {'name': 'Çay', 'description': 'Türk çayı', 'price': 5.00, 'category': 'içecek'},
            {'name': 'Kahve', 'description': 'Türk kahvesi', 'price': 12.00, 'category': 'içecek'},
            {'name': 'Coca Cola', 'description': 'Soğuk içecek', 'price': 8.00, 'category': 'içecek'},
            {'name': 'Su', 'description': 'Doğal su', 'price': 3.00, 'category': 'içecek'},

            # Salatalar
            {'name': 'Çoban Salatası', 'description': 'Domates, salatalık, soğan, maydanoz', 'price': 15.00, 'category': 'salata'},
            {'name': 'Mevsim Salatası', 'description': 'Mevsimlik yeşillikler', 'price': 12.00, 'category': 'salata'},
            {'name': 'Rus Salatası', 'description': 'Geleneksel rus salatası', 'price': 18.00, 'category': 'salata'},
        ]

        # Ürünleri ekle (tekrarlayan varsa atla)
        for product_data in sample_products:
            if not Product.query.filter_by(name=product_data['name']).first():
                product = Product(**product_data)
                db.session.add(product)

        # Değişiklikleri kaydet
        db.session.commit()



if __name__ == '__main__':
    init_database()
