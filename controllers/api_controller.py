"""
REST API Controller
===================
Uygulamanın REST API endpoint'lerini sağlayan Blueprint.

Endpoint'ler:
- GET /products: Tüm müsait ürünler (JSON)
- GET /products/<category>: Kategoriye göre ürünler (JSON)
- GET /tables: Tüm masalar (JSON) - Auth gerekli
- POST /table/<id>/status: Masa durumu güncelleme - Auth gerekli
- GET /order/<id>: Sipariş detayları (JSON) - Auth gerekli
- POST /order/<id>/status: Sipariş durumu güncelleme - Auth gerekli
- GET /search: Ürün arama (query param: q)

Özellikler:
- @require_auth decorator: Hem admin hem user girişini kabul eder
- JSON response formatı
- CORS desteği hazır
- Model.to_dict() metodları ile serialize

Kullanım:
    GET /api/products
    GET /api/products/yemek
    GET /api/search?q=pizza
"""

from flask import Blueprint, jsonify, request, flash, redirect, url_for
from extensions import db
from models import Product, Order, Table
from utils.dual_auth import is_admin_logged_in, is_user_logged_in

# SOLID: Service'leri import et
from domain import ProductService, OrderService, TableService

api_bp = Blueprint('api', __name__)

# Service instance'ları oluştur
product_service = ProductService()
order_service = OrderService()
table_service = TableService()

def require_auth(f):
    """API için hem admin hem user girişi kabul eden decorator"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (is_admin_logged_in() or is_user_logged_in()):
            return jsonify({'success': False, 'message': 'Giriş yapmalısınız!'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/products')
def get_products():
    """Tüm ürünleri JSON olarak döndür - SOLID: ProductService kullanarak"""
    products = product_service.get_available_products()
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/products/<category>')
def get_products_by_category(category):
    """Kategoriye göre ürünleri döndür - SOLID: ProductService kullanarak"""
    products = product_service.get_products_by_category(category, available_only=True)
    return jsonify([product.to_dict() for product in products])

@api_bp.route('/tables')
@require_auth
def get_tables():
    """Tüm masaları JSON olarak döndür - SOLID: TableService kullanarak"""
    tables = table_service.get_all_tables()
    return jsonify([table.to_dict() for table in tables])

@api_bp.route('/table/<int:table_id>/status', methods=['POST'])
@require_auth
def update_table_status(table_id):
    """Masa dolu/boş durumunu güncelle - SOLID: TableService kullanarak"""
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
    """Sipariş detaylarını döndür - SOLID: OrderService kullanarak"""
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Sipariş bulunamadı!'}), 404
    return jsonify(order.to_dict())

@api_bp.route('/order/<int:order_id>/status', methods=['POST'])
@require_auth
def update_order_status(order_id):
    """Sipariş durumunu güncelle (admin) - SOLID: OrderService kullanarak"""
    order = order_service.get_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Sipariş bulunamadı!'}), 404
    
    new_status = request.form.get('status')
    if new_status not in ['pending', 'completed', 'payment_pending', 'paid', 'cancelled']:
        return jsonify({'success': False, 'message': 'Geçersiz durum!'}), 400
    
    # Status'e göre uygun service metodunu çağır
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
    """Ürün arama - SOLID: ProductService kullanarak"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # ProductService'te search metodu eklenebilir, şimdilik repository üzerinden
    from models import Product
    products = Product.query.filter(
        Product.name.contains(query),
        Product.is_available == True
    ).all()
    
    return jsonify([product.to_dict() for product in products])
