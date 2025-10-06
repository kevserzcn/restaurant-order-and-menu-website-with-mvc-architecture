from flask_login import UserMixin
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    
    def __init__(self, phone, name):
        self.phone = phone
        self.name = name
    
    def get_id(self):
        return str(self.id)
    
    def check_password(self, password):
        """For user authentication, we use name as password"""
        return self.name == password
    
    def __repr__(self):
        return f'<User {self.phone}>'
