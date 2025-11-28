"""
Table Repository
================
Masa veritabanı işlemleri.

SOLID: Single Responsibility - Sadece Table CRUD
"""

from typing import List, Optional
from models.table import Table
from .base_repository import BaseRepository

class TableRepository(BaseRepository[Table]):
    """Masa repository"""
    
    def __init__(self):
        super().__init__(Table)
    
    def get_available_tables(self) -> List[Table]:
        """Boş masaları getir"""
        return self.filter_by(is_occupied=False)
    
    def get_occupied_tables(self) -> List[Table]:
        """Dolu masaları getir"""
        return self.filter_by(is_occupied=True)
    
    def get_by_name(self, name: str) -> Optional[Table]:
        """İsme göre masa bul"""
        return self.first_by(name=name)
    
    def set_occupied(self, table_id: int, is_occupied: bool) -> bool:
        """Masa doluluk durumunu ayarla"""
        table = self.get_by_id(table_id)
        if table:
            table.is_occupied = is_occupied
            self.save(table)
            return True
        return False
    
    def count_available(self) -> int:
        """Boş masa sayısını say"""
        return self.model.query.filter_by(is_occupied=False).count()
    
    def count_occupied(self) -> int:
        """Dolu masa sayısını say"""
        return self.model.query.filter_by(is_occupied=True).count()
