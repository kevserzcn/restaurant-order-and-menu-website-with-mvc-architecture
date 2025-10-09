#!/usr/bin/env python3
"""
Database initialization script for Restaurant Menu System (Custom Menu)
"""

from app import create_app
from extensions import db
from models import Product, Admin, User, Table
from werkzeug.security import generate_password_hash


def init_database():
    """Initialize database with categories, menu items, and default admin"""
    app = create_app()

    with app.app_context():
        db.create_all()

        # --- Varsayılan admin ---
        if not Admin.query.filter_by(email='admin@restaurant.com').first():
            admin = Admin(
                email='admin@restaurant.com',
                password=generate_password_hash('admin123'),
                name='Admin'
            )
            db.session.add(admin)
            print("✓ Default admin created")

        # --- Örnek kullanıcı ---
        if not User.query.filter_by(email='musteri@example.com').first():
            user = User(email='musteri@example.com', name='Misafir')
            db.session.add(user)
            print("✓ Sample user created")

        # --- Menü kategorileri ve ürünleri ---
        sample_products = [
            # 🍽️ YEMEKLER
            {'name': 'Güneş Pilavı', 'description': 'Güneş gibi parlayan lezzetli tereyağlı pilav', 'price': 60.00, 'category': 'yemek', 'image_url': 'GunesPilav.png'},
            {'name': 'Deniz Esintisi Lokmaları', 'description': 'Deniz ürünlerinden özel soslarla hazırlanmış lokmalar', 'price': 85.00, 'category': 'yemek', 'image_url': 'DenizEsintisiLokma.png'},
            {'name': "Ege'nin Balığı", 'description': 'Taptaze Ege usulü ızgara balık', 'price': 95.00, 'category': 'yemek', 'image_url': 'EgeBalik.png'},
            {'name': 'Anne Eli Spagetti', 'description': 'Anne eli değmiş ev yapımı spagetti', 'price': 70.00, 'category': 'yemek', 'image_url': 'Spagetti.png'},
            {'name': 'Bamya Çorbası', 'description': 'Anadolu’nun klasiklerinden bamya çorbası', 'price': 45.00, 'category': 'yemek', 'image_url': 'BamyaCorbasi.png'},

            # 🍰 TATLILAR
            {'name': 'Dreamisu', 'description': 'Rüya gibi hafif tiramisu lezzeti', 'price': 50.00, 'category': 'tatlı', 'image_url': 'Dreamisu.png'},
            {'name': 'Altın Yaprak Baklava', 'description': 'Gerçek altın yapraklı özel baklava', 'price': 65.00, 'category': 'tatlı', 'image_url': 'Baklava.png'},
            {'name': 'Günbatımı Sütlacı', 'description': 'Nar gibi kızarmış üstüyle geleneksel sütlaç', 'price': 40.00, 'category': 'tatlı', 'image_url': 'GunbatimiSutlac.png'},

            # 🥤 İÇECEKLER
            {'name': 'Tatlı Esintisi', 'description': 'Meyveli tatlı içecek karışımı', 'price': 30.00, 'category': 'içecek', 'image_url': 'TatliEsintisi.png'},
            {'name': 'Anne Limonata', 'description': 'Ev yapımı taze limonata', 'price': 25.00, 'category': 'içecek', 'image_url': 'AnneLimonata.png'},
            {'name': 'Turuncu Ufuk', 'description': 'Portakal ve mango esintili özel içecek', 'price': 28.00, 'category': 'içecek', 'image_url': 'TuruncuUfuk.png'},
            {'name': 'Mavi Düş', 'description': 'Yaban mersinli serinletici içecek', 'price': 32.00, 'category': 'içecek', 'image_url': 'MaviDus.png'},
            {'name': 'Yeşil Meltem', 'description': 'Nane ve lime aromalı taze içecek', 'price': 29.00, 'category': 'içecek', 'image_url': 'YesilMeltem.png'},

            # 🥗 SALATALAR
            {'name': 'Közde Mucize', 'description': 'Közlenmiş sebzelerden oluşan nefis karışım', 'price': 40.00, 'category': 'salata', 'image_url': 'KozdeMucize.png'},
            {'name': 'Çoban Salatası', 'description': 'Geleneksel taze malzemeli çoban salatası', 'price': 35.00, 'category': 'salata', 'image_url': 'CobanSalatasi.png'},
            {'name': 'Akdeniz Esintisi', 'description': 'Zeytinyağlı Akdeniz yeşillikleriyle hazırlanmış salata', 'price': 38.00, 'category': 'salata', 'image_url': 'AkdenizEsintisi.png'},
        ]

        # --- Ürünleri ekle (daha önce eklenmediyse) ---
        for data in sample_products:
            if not Product.query.filter_by(name=data['name']).first():
                db.session.add(Product(**data))

        # --- Masalar (1-10) ---
        for num in range(1, 13):
            if not Table.query.filter_by(table_number=num).first():
                db.session.add(Table(table_number=num, capacity=4))

        db.session.commit()
        print("✓ Database initialized with full custom menu!")


if __name__ == '__main__':
    init_database()
