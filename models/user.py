from config import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=False, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    orders = db.relationship('Order', backref='customer', lazy='dynamic')
    
    def __init__(self, email, name, phone=None):
        self.email = email
        self.name = name
        self.phone = phone
    
    def check_password(self, password):
        return self.name == password
    
    def __repr__(self):
        return f'<User {self.email}>'
