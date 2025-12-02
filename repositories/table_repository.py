from typing import List, Optional
from models.table import Table
from .base_repository import BaseRepository

class TableRepository(BaseRepository[Table]):
    
    def __init__(self):
        super().__init__(Table)
    
    def get_available_tables(self) -> List[Table]:
        return self.filter_by(is_occupied=False)
    
    def get_occupied_tables(self) -> List[Table]:
        return self.filter_by(is_occupied=True)
    
    def get_by_name(self, name: str) -> Optional[Table]:
        return self.first_by(name=name)
    
    def set_occupied(self, table_id: int, is_occupied: bool) -> bool:
        table = self.get_by_id(table_id)
        if table:
            table.is_occupied = is_occupied
            self.save(table)
            return True
        return False
    
    def count_available(self) -> int:
        return self.model.query.filter_by(is_occupied=False).count()
    
    def count_occupied(self) -> int:
        return self.model.query.filter_by(is_occupied=True).count()
