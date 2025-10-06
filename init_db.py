#!/usr/bin/env python3
"""
Database initialization script for Restaurant Menu System
"""

from app import create_app
from extensions import db
from models import User, Admin, Product, Table

def init_database():
    """Initialize database with sample data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(email='admin@restaurant.com').first():
            admin = Admin(
                email='admin@restaurant.com',
                password='admin123',
                name='Admin'
            )
            db.session.add(admin)
            print("✓ Default admin created")
        
        # Create sample products
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
        
        for product_data in sample_products:
            if not Product.query.filter_by(name=product_data['name']).first():
                product = Product(**product_data)
                db.session.add(product)
        
        # Create sample tables
        for i in range(1, 11):  # 10 masa
            if not Table.query.filter_by(table_number=i).first():
                table = Table(
                    table_number=i,
                    capacity=4 if i <= 5 else 6,  # İlk 5 masa 4 kişilik, sonraki 5 masa 6 kişilik
                    waiter_name=f'Garson {i}' if i <= 5 else None
                )
                db.session.add(table)
        
        # Create sample users
        sample_users = [
            {'phone': '05551234567', 'name': 'Ahmet Yılmaz'},
            {'phone': '05559876543', 'name': 'Fatma Demir'},
            {'phone': '05555555555', 'name': 'Mehmet Kaya'},
        ]
        
        for user_data in sample_users:
            if not User.query.filter_by(phone=user_data['phone']).first():
                user = User(**user_data)
                db.session.add(user)
        
        # Commit all changes
        db.session.commit()
        
        print("✓ Database initialized successfully!")
        print("✓ Sample data created:")
        print(f"  - {Product.query.count()} products")
        print(f"  - {Table.query.count()} tables")
        print(f"  - {User.query.count()} users")
        print(f"  - {Admin.query.count()} admins")
        print("\nDefault admin credentials:")
        print("  Email: admin@restaurant.com")
        print("  Password: admin123")

if __name__ == '__main__':
    init_database()
