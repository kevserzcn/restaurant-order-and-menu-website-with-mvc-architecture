from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import Product, Order, Table

api_bp = Blueprint('api', __name__)

@api_bp.route('/products')
def get_products():
    """Tüm ürünleri JSON olarak döndür"""
    products = Product.query.filter_by(is_available=True).all()
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/products/<category>')
def get_products_by_category(category):
    """Kategoriye göre ürünleri döndür"""
    products = Product.query.filter_by(category=category, is_available=True).all()
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/tables')
@login_required
def get_tables():
    """Tüm masaları JSON olarak döndür"""
    tables = Table.query.all()
    return jsonify([table.to_dict() for table in tables])

@api_bp.route('/order/<int:order_id>')
@login_required
def get_order(order_id):
    """Sipariş detaylarını döndür"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@api_bp.route('/search')
def search_products():
    """Ürün arama"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    products = Product.query.filter(
        Product.name.contains(query),
        Product.is_available == True
    ).all()
    
    return jsonify([product.to_dict() for product in products])
