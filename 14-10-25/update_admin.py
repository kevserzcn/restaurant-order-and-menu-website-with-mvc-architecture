#!/usr/bin/env python3
"""
Admin kullanıcı adını güncelleyen script
"""

from app import create_app
from extensions import db
from models import Admin

def update_admin_name():
    """ID=1 olan admin kullanıcısının adını 'Ablalar' olarak güncelle"""
    app = create_app()

    with app.app_context():
        # ID=1 olan admin'i bul
        admin = Admin.query.get(1)
        
        if admin:
            old_name = admin.name
            admin.name = 'Ablalar'
            db.session.commit()
            print(f"✓ Admin güncellendi: '{old_name}' → '{admin.name}'")
            print(f"  Email: {admin.email}")
            print(f"  ID: {admin.id}")
        else:
            print("✗ ID=1 olan admin bulunamadı!")
            
            # Tüm adminleri listele
            all_admins = Admin.query.all()
            if all_admins:
                print("\n📋 Mevcut adminler:")
                for a in all_admins:
                    print(f"  - ID: {a.id}, İsim: {a.name}, Email: {a.email}")
            else:
                print("✗ Hiç admin bulunamadı!")

if __name__ == '__main__':
    update_admin_name()
