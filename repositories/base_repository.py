from typing import TypeVar, Generic, List, Optional
from config import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    
    def __init__(self, model_class: type):
        self.model = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        return self.model.query.get(id)
    
    def get_all(self) -> List[T]:
        return self.model.query.all()
    
    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance
    
    def delete(self, instance: T) -> bool:
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Delete error: {str(e)}")
            return False
    
    def save(self, instance: T) -> T:
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def filter_by(self, **kwargs) -> List[T]:
        return self.model.query.filter_by(**kwargs).all()
    
    def first_by(self, **kwargs) -> Optional[T]:
        return self.model.query.filter_by(**kwargs).first()
