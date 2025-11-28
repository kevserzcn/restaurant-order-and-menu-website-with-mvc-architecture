"""
İletişim/Yorum Modeli
=====================
Müşterilerden gelen iletişim, şikayet, yorum ve puanları saklar.

Alanlar:
- id: İletişim kaydı kimliği
- user_id: İletişimde bulunan kullanıcı (opsiyonel - anonim olabilir)
- name: Kullanıcı adı
- email: E-posta adresi
- type: İletişim tipi (request/complaint/comment)
- message: Mesaj içeriği
- rating: Puan (1-5 yıldız)
- is_visible: Diğer kullanıcılar tarafından görülebilir mi?
- created_at: Oluşturulma zamanı
"""

from extensions import db
from datetime import datetime

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # request, complaint, comment
    message = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 yıldız
    is_visible = db.Column(db.Boolean, default=True)  # Diğer kullanıcılar görebilir mi?
    reply = db.Column(db.Text, nullable=True)  # Admin cevabı
    replied_at = db.Column(db.DateTime, nullable=True)  # Cevap tarihi
    replied_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)  # Cevap veren admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='contacts', lazy='joined')
    admin_replier = db.relationship('Admin', foreign_keys=[replied_by], lazy='joined')
    
    def __init__(self, name, email, type, message, rating=None, user_id=None, is_visible=True, reply=None, replied_by=None):
        self.name = name
        self.email = email
        self.type = type
        self.message = message
        self.rating = rating
        self.user_id = user_id
        self.is_visible = is_visible
        self.reply = reply
        self.replied_by = replied_by
        if reply and not self.replied_at:
            self.replied_at = datetime.utcnow()
    
    def get_type_display(self):
        """İletişim tipini Türkçe olarak döndür"""
        types = {
            'request': 'İstek',
            'complaint': 'Şikayet',
            'comment': 'Yorum'
        }
        return types.get(self.type, self.type)
    
    def get_rating_stars(self):
        """Puanı yıldız olarak döndür (HTML için)"""
        if not self.rating:
            return 0
        return self.rating
    
    def to_dict(self):
        """JSON serialization için dictionary'ye çevir"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'type': self.type,
            'type_display': self.get_type_display(),
            'message': self.message,
            'rating': self.rating,
            'is_visible': self.is_visible,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Contact {self.id}: {self.type} by {self.name}>'

