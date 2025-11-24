"""
User Repository
===============
Kullanıcı veritabanı işlemleri.

SOLID: Single Responsibility - Sadece User CRUD
"""

from typing import Optional
from models.user import User
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """Kullanıcı repository"""
    
    def __init__(self):
        super().__init__(User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        """E-posta ile kullanıcı bul"""
        return self.first_by(email=email)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """E-posta ile kullanıcı bul (alias)"""
        return self.find_by_email(email)
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Telefon ile kullanıcı bul"""
        return self.first_by(phone=phone)
    
    def email_exists(self, email: str) -> bool:
        """E-posta kayıtlı mı kontrol et"""
        return self.find_by_email(email) is not None
    
    def phone_exists(self, phone: str) -> bool:
        """Telefon kayıtlı mı kontrol et"""
        return self.get_by_phone(phone) is not None
    
    def create_user(self, email: str, name: str) -> User:
        """Yeni kullanıcı oluştur"""
        from extensions import db
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()
        return user
