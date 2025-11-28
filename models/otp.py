"""
OTP (One-Time Password) Modeli
===============================
Şifre sıfırlama için geçici kod saklama.

Alanlar:
- id: OTP kimliği
- email: E-posta adresi
- code: OTP kodu (6 haneli)
- expires_at: Kodun geçerlilik süresi
- used: Kod kullanıldı mı?
- created_at: Oluşturulma zamanı
"""

from extensions import db
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
        """Kod geçerli mi kontrol et"""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def mark_as_used(self):
        """Kodu kullanıldı olarak işaretle"""
        self.used = True
        db.session.commit()
    
    def __repr__(self):
        return f'<OTP {self.email}: {self.code}>'



