"""
Ablaların Yeri - Restoran Yönetim Sistemi

Ana Flask Uygulama Dosyası
============================================
Bu dosya Flask uygulamasının temel yapılandırmasını ve başlatılmasını içerir.

Özellikler:
- Flask app factory pattern ile uygulama oluşturma
- Dual authentication sistemi (Admin ve User aynı anda giriş yapabilir)
- Blueprint'lerin (auth, admin, user, api) kaydedilmesi
- Veritabanı tablolarının otomatik oluşturulması
- Template context processor ile auth bilgilerinin tüm sayfalara enjeksiyonu
- Jinja2 custom filter'ları (datetime formatları)
- Default admin kullanıcısının otomatik oluşturulması

Kullanım:
    python app.py              # Development server başlat
    docker-compose up          # Docker ile çalıştır
"""

import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db
from models import User, Admin, Product, Order, OrderItem, Table, Payment
from controllers import auth_bp, admin_bp, user_bp, api_bp
from utils import format_local

def create_app():
    app = Flask(__name__, template_folder='views')
    app.config.from_object(Config)

    # Ensure the instance folder exists for SQLite on local environments
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(api_bp, url_prefix='/api')

    def datetime_tr(value, fmt='%d.%m.%Y %H:%M'):
        if not value:
            return ''
        return format_local(value, fmt)

    app.jinja_env.filters['datetime_tr'] = datetime_tr

    # Context processor for dual authentication
    @app.context_processor
    def inject_auth():
        """Template'lerde kullanılacak auth bilgilerini enjekte et"""
        from utils.dual_auth import get_current_admin, get_current_user_custom, is_admin_logged_in, is_user_logged_in
        from flask import request
        
        current_admin = get_current_admin()
        current_user_custom = get_current_user_custom()
        
        # Hangi sayfada olduğumuza göre current_user'ı belirle
        path = request.path
        
        if path.startswith('/admin/'):
            # Admin sayfasındayız, admin'i göster
            current_user = current_admin
        elif path.startswith('/user/'):
            # User sayfasındayız, user'ı göster
            current_user = current_user_custom
        else:
            # Diğer sayfalarda kim login olduysa onu göster
            current_user = current_admin or current_user_custom
        
        return {
            'current_user': current_user,
            'current_admin': current_admin,
            'current_user_custom': current_user_custom,
            'is_admin_logged_in': is_admin_logged_in(),
            'is_user_logged_in': is_user_logged_in()
        }

    # Root route -> show main index
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
        # Basit şema göçü: users tablosunda email kolonu yoksa ekle
        try:
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            if 'email' not in columns:
                db.session.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120)"))
                db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
                db.session.commit()
        except Exception:
            # Sessiz geç - farklı veritabanlarında PRAGMA yoktur, manuel migration kullanılabilir
            pass
        
        # Basit şema göçü: contacts tablosuna yeni kolonlar ekle
        try:
            from sqlalchemy import text
            result = db.session.execute(text("PRAGMA table_info(contacts)"))
            columns = [row[1] for row in result]
            
            if 'reply' not in columns:
                db.session.execute(text("ALTER TABLE contacts ADD COLUMN reply TEXT"))
            if 'replied_at' not in columns:
                db.session.execute(text("ALTER TABLE contacts ADD COLUMN replied_at DATETIME"))
            if 'replied_by' not in columns:
                db.session.execute(text("ALTER TABLE contacts ADD COLUMN replied_by INTEGER"))
                db.session.execute(text("CREATE INDEX IF NOT EXISTS ix_contacts_replied_by ON contacts (replied_by)"))
            
            db.session.commit()
        except Exception as e:
            # Sessiz geç - farklı veritabanlarında PRAGMA yoktur, manuel migration kullanılabilir
            print(f"Migration warning: {e}")
            pass
        
        # Create default admin if not exists
        if not Admin.query.filter_by(email='admin@restaurant.com').first():
            admin = Admin(
                email='admin@restaurant.com',
                password='admin123',
                name='Admin'
            )
            db.session.add(admin)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
