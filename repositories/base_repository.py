"""
Base Repository
===============
Tüm repository'lerin miras aldığı temel sınıf.

SOLID: Single Responsibility - Sadece CRUD işlemleri
"""

from typing import TypeVar, Generic, List, Optional
from extensions import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Temel repository sınıfı - genel CRUD işlemleri"""
    
    def __init__(self, model_class: type):
        self.model = model_class
    
    def get_by_id(self, id: int) -> Optional[T]:
        """ID'ye göre kayıt getir"""
        return self.model.query.get(id)
    
    def get_all(self) -> List[T]:
        """Tüm kayıtları getir"""
        return self.model.query.all()
    
    def create(self, **kwargs) -> T:
        """Yeni kayıt oluştur"""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, instance: T, **kwargs) -> T:
        """Kayıt güncelle"""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance
    
    def delete(self, instance: T) -> bool:
        """Kayıt sil"""
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def save(self, instance: T) -> T:
        """Değişiklikleri kaydet"""
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def filter_by(self, **kwargs) -> List[T]:
        """Filtreye göre kayıtları getir"""
        return self.model.query.filter_by(**kwargs).all()
    
    def first_by(self, **kwargs) -> Optional[T]:
        """Filtreye göre ilk kaydı getir"""
        return self.model.query.filter_by(**kwargs).first()
