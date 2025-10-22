import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager
from models import User, Admin, Product, Order, OrderItem, Table, Payment
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from controllers.api_controller import api_bp
from utils.datetime_utils import format_local

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the instance folder exists for SQLite on local environments
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.index'
    login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
    login_manager.login_message_category = 'info'

    # Register user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Try to load from User first, then Admin
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return None
        user = User.query.get(uid)
        if user:
            return user
        return Admin.query.get(uid)
    
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
