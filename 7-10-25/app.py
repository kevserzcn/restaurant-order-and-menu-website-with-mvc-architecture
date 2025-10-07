from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager
from models import User, Admin, Product, Order, OrderItem, Table, Payment
from controllers.auth_controller import auth_bp
from controllers.admin_controller import admin_bp
from controllers.user_controller import user_bp
from controllers.api_controller import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
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

    # Root route -> show main index
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
        
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
