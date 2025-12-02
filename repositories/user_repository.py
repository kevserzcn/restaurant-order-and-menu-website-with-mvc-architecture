from typing import Optional
from models.user import User
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    
    def __init__(self):
        super().__init__(User)
    
    def find_by_email(self, email: str) -> Optional[User]:
        return self.first_by(email=email)
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.find_by_email(email)
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.first_by(phone=phone)
    
    def create_user(self, email: str, name: str) -> User:
        from config import db
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()
        return user
