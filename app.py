import os
from flask import Flask, render_template, request
from config import Config
from config import db
from controllers import auth_bp, admin_bp, user_bp, api_bp
from utils import format_local
from utils.dual_auth import get_current_admin, get_current_user_custom, is_admin_logged_in, is_user_logged_in

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
        return render_template('index.html')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
