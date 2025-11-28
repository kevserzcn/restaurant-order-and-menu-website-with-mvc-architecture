"""
Admin Repository
================
Admin kullanıcı veritabanı işlemleri.

SOLID: Single Responsibility - Sadece Admin CRUD
"""

from typing import Optional
from models.admin import Admin
from .base_repository import BaseRepository

class AdminRepository(BaseRepository[Admin]):
    """Admin repository"""
    
    def __init__(self):
        super().__init__(Admin)
    
    def find_by_email(self, email: str) -> Optional[Admin]:
        """E-posta ile admin bul"""
        return self.first_by(email=email)
    
    def get_by_email(self, email: str) -> Optional[Admin]:
        """E-posta ile admin bul (alias)"""
        return self.find_by_email(email)
    
    def email_exists(self, email: str) -> bool:
        """E-posta kayıtlı mı kontrol et"""
        return self.find_by_email(email) is not None
