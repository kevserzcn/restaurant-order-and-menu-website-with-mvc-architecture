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

@api_bp.route('/table/<int:table_id>/status', methods=['POST'])
@login_required
def update_table_status(table_id):
    """Masa dolu/boş durumunu güncelle"""
    table = Table.query.get_or_404(table_id)
    status = request.form.get('status')
    if status not in ['occupied', 'empty']:
        return jsonify({'success': False, 'message': 'Geçersiz durum!'}), 400
    table.is_occupied = (status == 'occupied')
    db.session.commit()
    return jsonify({'success': True, 'message': 'Masa durumu güncellendi.'})

@api_bp.route('/order/<int:order_id>')
@login_required
def get_order(order_id):
    """Sipariş detaylarını döndür"""
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())

@api_bp.route('/order/<int:order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Sipariş durumunu güncelle (admin)"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status not in ['pending', 'completed', 'payment_pending', 'paid', 'cancelled']:
        return jsonify({'success': False, 'message': 'Geçersiz durum!'}), 400
    order.status = new_status
    db.session.commit()
    return jsonify({'success': True, 'message': 'Durum güncellendi.'})

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
