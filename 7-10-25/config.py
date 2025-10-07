import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///restaurant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration for SMS/PDF sending
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # SMS API configuration
    SMS_API_KEY = os.environ.get('SMS_API_KEY')
    SMS_API_URL = os.environ.get('SMS_API_URL')
    
    # Pagination
    POSTS_PER_PAGE = 10
