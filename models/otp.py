from config import db
from datetime import datetime, timedelta

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, email, code, expires_in_minutes=10):
        self.email = email
        self.code = code
        self.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        self.used = False
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        self.used = True
        db.session.commit()
    
    def __repr__(self):
        return f'<OTP {self.email}: {self.code}>'



