"""
User Validator
==============
Kullanıcı business validation.

SOLID: Single Responsibility - Sadece kullanıcı validasyonu
"""

from typing import Optional
import re

class UserValidator:
    """Kullanıcı validator"""
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        """E-posta validasyonu"""
        if not email or len(email.strip()) == 0:
            return False, "E-posta adresi boş olamaz"
        
        # Basit e-posta regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Geçersiz e-posta adresi formatı"
        
        if len(email) > 120:
            return False, "E-posta adresi en fazla 120 karakter olabilir"
        
        return True, None
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, Optional[str]]:
        """İsim validasyonu"""
        if not name or len(name.strip()) == 0:
            return False, "İsim boş olamaz"
        
        if len(name) < 2:
            return False, "İsim en az 2 karakter olmalıdır"
        
        if len(name) > 100:
            return False, "İsim en fazla 100 karakter olabilir"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, Optional[str]]:
        """Telefon validasyonu"""
        if not phone:
            return True, None  # Telefon opsiyonel
        
        phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if not phone_clean.isdigit():
            return False, "Telefon numarası sadece rakamlardan oluşmalıdır"
        
        if len(phone_clean) != 10 and len(phone_clean) != 11:
            return False, "Telefon numarası 10 veya 11 haneli olmalıdır"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, Optional[str]]:
        """Şifre validasyonu"""
        if not password:
            return False, "Şifre boş olamaz"
        
        if len(password) < 6:
            return False, "Şifre en az 6 karakter olmalıdır"
        
        if len(password) > 100:
            return False, "Şifre en fazla 100 karakter olabilir"
        
        return True, None
