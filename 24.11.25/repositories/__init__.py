"""
Repository Layer
================
Veritabanı işlemlerini soyutlayan repository sınıfları.

SOLID Prensibi: Dependency Inversion Principle (DIP)
- Controller'lar model'lere doğrudan bağımlı değil
- Repository interface üzerinden çalışır
"""

from .base_repository import BaseRepository
from .product_repository import ProductRepository
from .order_repository import OrderRepository
from .table_repository import TableRepository
from .user_repository import UserRepository
from .payment_repository import PaymentRepository
from .admin_repository import AdminRepository

__all__ = [
    'BaseRepository',
    'ProductRepository',
    'OrderRepository',
    'TableRepository',
    'UserRepository',
    'PaymentRepository',
    'AdminRepository'
]
