from typing import List, Dict, Optional
from repositories import ContactRepository
from models.contact import Contact
from datetime import datetime
from services.email_service import send_reply_email
from config import db

class ContactService:
    
    def __init__(self):
        self.contact_repo = ContactRepository()
    
    def get_all_contacts(self) -> List[Contact]:
        return self.contact_repo.get_all_ordered_by_date()
    
    def get_visible_comments(self) -> List[Contact]:
        return self.contact_repo.get_visible_comments()
    
    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        return self.contact_repo.get_by_id(contact_id)
    
    def create_contact(self, name: str, email: str, contact_type: str, 
                      message: str, rating: Optional[int] = None, 
                      user_id: Optional[int] = None, 
                      is_visible: bool = True) -> Contact:
        return self.contact_repo.create(
            name=name,
            email=email,
            type=contact_type,
            message=message,
            rating=rating,
            user_id=user_id,
            is_visible=is_visible
        )
    
    def reply_to_contact(self, contact_id: int, reply_text: str, 
                        admin_id: int, admin_name: str) -> Optional[Contact]:
        contact = self.contact_repo.get_by_id(contact_id)
        if not contact:
            return None
        
        contact.reply = reply_text
        contact.replied_at = datetime.utcnow()
        contact.replied_by = admin_id
        db.session.commit()
        
        send_reply_email(
            recipient_email=contact.email,
            contact_name=contact.name,
            contact_type=contact.type,
            original_message=contact.message,
            admin_reply=reply_text,
            admin_name=admin_name
        )
        
        return contact
    
    def get_statistics(self) -> Dict:
        all_contacts = self.contact_repo.get_all()
        
        total_contacts = len(all_contacts)
        comments = [c for c in all_contacts if c.type == 'comment']
        requests = [c for c in all_contacts if c.type == 'request']
        complaints = [c for c in all_contacts if c.type == 'complaint']
        replied_count = len([c for c in all_contacts if c.reply])
        pending_replies = len([c for c in all_contacts if not c.reply])
        
        ratings = [c.rating for c in comments if c.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            'total_contacts': total_contacts,
            'comments_count': len(comments),
            'requests_count': len(requests),
            'complaints_count': len(complaints),
            'replied_count': replied_count,
            'pending_replies': pending_replies,
            'avg_rating': round(avg_rating, 1)
        }
