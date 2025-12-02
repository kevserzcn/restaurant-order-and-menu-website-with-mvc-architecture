from typing import List, Optional
from repositories import TableRepository, OrderRepository
from models.table import Table

class TableService:
    
    def __init__(self):
        self.table_repo = TableRepository()
        self.order_repo = OrderRepository()
    
    def create_table(self, name: str, capacity: int = 4) -> Table:
        if self.table_repo.get_by_name(name):
            raise ValueError(f"Bu masa adı zaten mevcut: {name}")
        
        return self.table_repo.create(name=name, capacity=capacity)
    
    def get_table(self, table_id: int) -> Optional[Table]:
        return self.table_repo.get_by_id(table_id)
    
    def get_table_by_id(self, table_id: int) -> Optional[Table]:
        return self.get_table(table_id)
    
    def get_all_tables(self) -> List[Table]:
        return self.table_repo.get_all()
    
    def get_available_tables(self) -> List[Table]:
        return self.table_repo.get_available_tables()
    
    def get_occupied_tables(self) -> List[Table]:
        return self.table_repo.get_occupied_tables()
    
    def occupy_table(self, table_id: int) -> bool:
        return self.table_repo.set_occupied(table_id, True)
    
    def release_table(self, table_id: int) -> bool:
        return self.table_repo.set_occupied(table_id, False)
    
    def update_table(self, table_id: int, name: Optional[str] = None, capacity: Optional[int] = None) -> Optional[Table]:
        table = self.table_repo.get_by_id(table_id)
        if not table:
            return None
        
        update_data = {}
        if name:
            existing = self.table_repo.get_by_name(name)
            if existing and existing.id != table_id:
                raise ValueError(f"Bu masa adı zaten mevcut: {name}")
            update_data['name'] = name
        
        if capacity:
            update_data['capacity'] = capacity
        
        return self.table_repo.update(table, **update_data)
    
    def delete_table(self, table_id: int) -> bool:
        table = self.table_repo.get_by_id(table_id)
        if not table:
            return False
        
        active_order = self.order_repo.get_current_by_table(table_id)
        if active_order:
            raise ValueError("Masada aktif sipariş var, silinemez!")
        
        return self.table_repo.delete(table)
    
    def get_table_total_amount(self, table_id: int) -> float:
        current_order = self.order_repo.get_current_by_table(table_id)
        if current_order:
            if current_order.total_amount == 0 and current_order.items.count() > 0:
                total = sum(item.quantity * item.price for item in current_order.items.all())
                current_order.total_amount = total
                self.order_repo.save(current_order)
            return current_order.total_amount
        return 0.0
    
    def get_table_stats(self):
        return {
            'total': len(self.table_repo.get_all()),
            'occupied': self.table_repo.count_occupied(),
            'available': self.table_repo.count_available()
        }
