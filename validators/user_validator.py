from typing import List, Optional
import re

class UserValidator:
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        if not email or len(email.strip()) == 0:
            return False, "E-posta adresi boş olamaz"
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False, "Geçersiz e-posta adresi formatı"
        
        if len(email) > 120:
            return False, "E-posta adresi en fazla 120 karakter olabilir"
        
        return True, None
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, Optional[str]]:
        if not name or len(name.strip()) == 0:
            return False, "İsim boş olamaz"
        
        if len(name) < 2:
            return False, "İsim en az 2 karakter olmalıdır"
        
        if len(name) > 100:
            return False, "İsim en fazla 100 karakter olabilir"
        
        return True, None
    
    @classmethod
    def validate_user_registration(cls, email: str, name: str) -> tuple[bool, List[str]]:
        errors = []
        
        is_valid, error = cls.validate_email(email)
        if not is_valid:
            errors.append(error)
        
        is_valid, error = cls.validate_name(name)
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors