from flask import Blueprint, jsonify, request
from config import db
from models import Product
from utils.dual_auth import is_admin_logged_in, is_user_logged_in

from services import ProductService, OrderService, TableService

api_bp = Blueprint('api', __name__)

product_service = ProductService()
order_service = OrderService()
table_service = TableService()

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (is_admin_logged_in() or is_user_logged_in()):
            return jsonify({'success': False, 'message': 'Giriş yapmalısınız!'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/products')
def get_products():
    products = product_service.get_available_products()
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/products/<category>')
def get_products_by_category(category):
    products = product_service.get_products_by_category(category, available_only=True)
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/tables')
@require_auth
def get_tables():
    tables = table_service.get_all_tables()
    return jsonify([table.to_dict() for table in tables])

@api_bp.route('/table/<int:table_id>/status', methods=['POST'])
@require_auth
def update_table_status(table_id):
    table = table_service.get_table_by_id(table_id)
    if not table:
        return jsonify({'success': False, 'message': 'Masa bulunamadı!'}), 404
    
    status = request.form.get('status')
    if status not in ['occupied', 'empty']:
        return jsonify({'success': False, 'message': 'Geçersiz durum!'}), 400
    
    if status == 'occupied':
        table_service.occupy_table(table_id)
    else:
        table_service.release_table(table_id)
    
    return jsonify({'success': True, 'message': 'Masa durumu güncellendi.'})

@api_bp.route('/order/<int:order_id>')
@require_auth
def get_order(order_id):
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Sipariş bulunamadı!'}), 404
    return jsonify(order.to_dict())

@api_bp.route('/order/<int:order_id>/status', methods=['POST'])
@require_auth
def update_order_status(order_id):
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Sipariş bulunamadı!'}), 404
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'completed', 'payment_pending', 'paid', 'cancelled']:
        return jsonify({'success': False, 'message': 'Geçersiz durum!'}), 400
    
    if new_status == 'cancelled':
        order_service.cancel_order(order_id)
    elif new_status == 'paid':
        order_service.mark_order_as_paid(order_id)
    else:
        order.status = new_status
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Durum güncellendi.'})

@api_bp.route('/search')
def search_products():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    products = Product.query.filter(
        Product.name.contains(query),
        Product.is_available == True
    ).all()
    
    return jsonify([product.to_dict() for product in products])
