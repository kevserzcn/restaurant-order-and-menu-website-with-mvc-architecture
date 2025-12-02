import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


db = SQLAlchemy()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'restaurant.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration for dual authentication
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 saat
    
    # Email configuration for invoice/PDF sending
    # Default to Gmail using the requested sender unless overridden via env
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'ablalar42@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max dosya boyutu
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Pagination
    POSTS_PER_PAGE = 10
