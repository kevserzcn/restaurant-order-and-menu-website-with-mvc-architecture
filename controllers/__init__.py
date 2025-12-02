from .admin_controller import admin_bp
from .user_controller import user_bp
from .auth_controller import auth_bp
from .api_controller import api_bp

__all__ = ['admin_bp', 'user_bp', 'auth_bp', 'api_bp']
