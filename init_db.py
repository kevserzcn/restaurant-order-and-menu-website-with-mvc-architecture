#!/usr/bin/env python3
"""
Veritabanı Başlatma Scripti
============================
Restaurant.db veritabanını sıfırdan oluşturup örnek verilerle dolduran script.

İçerik:
-------
1. Veritabanı tablolarını oluştur
2. Default admin kullanıcısı (admin@restaurant.com / admin123)
3. Örnek ürünler (yemek, tatlı, içecek, salata kategorilerinde)
4. Özel isimlendirilmiş masalar (yemek adlarıyla)

Örnek Ürünler:
--------------
- Yemekler: Akdeniz Esintisi, Balık Tabağı, vb.
- Tatlılar: Dreamisu, Günbatımı Sütlaç, vb.
- İçecekler: Anne Limonata, Mavi Duş, vb.
- Salatalar: Çoban Salatası, Peynir Tabağı, vb.

Örnek Masalar:
--------------
- Güneş Pilav, Spagetti, Deniz Esintisi Lokma, vb.
- Her masa 4-6 kişilik

Kullanım:
---------
    python init_db.py
    
    # Veya Flask app içinden
    from init_db import init_database
    init_database()

Uyarı:
------
Bu script mevcut veritabanını SİLER ve yeniden oluşturur!
Production ortamında dikkatli kullanın.
"""

from app import create_app
from extensions import db
from models import Product, Table, Admin

def init_database():
    """Initialize database with admin, menu items, and custom-named tables"""
    app = create_app()

    with app.app_context():
        # --- Veritabanı oluştur ---
        db.create_all()

        # --- Admin ekle ---
        if not Admin.query.filter_by(email='ablalar42@gmail.com').first():
            admin = Admin(
                email='ablalar42@gmail.com',
                password='ablalar42',
                name='Admin'
            )
            db.session.add(admin)
            print("✓ Default admin created")

        # --- Menü öğeleri ---
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

        # --- Menü ekleme ---
        added_count = 0
        for data in sample_products:
            if not Product.query.filter_by(name=data['name']).first():
                db.session.add(Product(**data))
                added_count += 1
        if added_count:
            db.session.commit()
            print(f"✓ {added_count} new menu items added successfully!")
        else:
            print("✓ Menu already up to date — no new items added.")

        # --- Masalar ---
        table_names = [
            "Müzehher", "Umman", "Feraye","Lili", "Elf's", "Küçük Prens",
            "Lavinia", "Dean Winchester", "Theo James", "Burhan Altıntop",
            "Niko", "Michael Scott", "Yalı", "Kevser", "Kutalmış"
        ]

        added_tables = 0
        for name in table_names:
            if not Table.query.filter_by(name=name).first():
                db.session.add(Table(name=name))
                added_tables += 1

        if added_tables:
            db.session.commit()
            print(f"✓ {added_tables} new tables added successfully!")
        else:
            print("✓ Tables already exist — no new tables added.")


if __name__ == '__main__':
    init_database()
