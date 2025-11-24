"""
Flask Uzantıları
================
Uygulama genelinde kullanılan Flask uzantılarının tanımlandığı dosya.

Uzantılar:
- SQLAlchemy (db): Veritabanı ORM işlemleri için

Not: Flask-Login kaldırıldı, yerine custom dual_auth sistemi kullanılıyor.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
