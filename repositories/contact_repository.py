from typing import List, Optional
from models.contact import Contact
from .base_repository import BaseRepository
from sqlalchemy import desc

class ContactRepository(BaseRepository[Contact]):
    
    def __init__(self):
        super().__init__(Contact)
    
    def get_all_ordered_by_date(self) -> List[Contact]:
        return self.model.query.order_by(desc(Contact.created_at)).all()
    
    def get_by_type(self, contact_type: str) -> List[Contact]:
        return self.model.query.filter_by(type=contact_type).all()
    
    def get_visible_comments(self) -> List[Contact]:
        return self.model.query.filter_by(
            is_visible=True,
            type='comment'
        ).order_by(desc(Contact.created_at)).all()
    
    def get_replied_contacts(self) -> List[Contact]:
        return self.model.query.filter(Contact.reply.isnot(None)).all()
    
    def get_pending_replies(self) -> List[Contact]:
        return self.model.query.filter(Contact.reply.is_(None)).all()
    
    def get_by_user_id(self, user_id: int) -> List[Contact]:
        return self.model.query.filter_by(user_id=user_id).all()

