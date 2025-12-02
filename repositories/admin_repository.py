from typing import Optional
from models.admin import Admin
from .base_repository import BaseRepository

class AdminRepository(BaseRepository[Admin]):
    
    def __init__(self):
        super().__init__(Admin)
    
    def find_by_email(self, email: str) -> Optional[Admin]:
        return self.first_by(email=email)
    
    def get_by_email(self, email: str) -> Optional[Admin]:
        return self.find_by_email(email)
