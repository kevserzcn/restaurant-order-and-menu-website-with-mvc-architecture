from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from extensions import db
from models import User, Product, Order, OrderItem, Table
from forms import OrderItemForm
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.before_request
def check_user():
    """Kullanıcı yetkisi kontrolü"""
    if not isinstance(current_user, User):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.login'))

@user_bp.route('/')
@user_bp.route('/dashboard')
@login_required
def dashboard():
    """Kullanıcı ana sayfa - menü görüntüleme"""
    # Kategorilere göre ürünleri getir
    yemekler = Product.query.filter_by(category='yemek', is_available=True).all()
    tatlilar = Product.query.filter_by(category='tatlı', is_available=True).all()
    icecekler = Product.query.filter_by(category='içecek', is_available=True).all()
    salatalar = Product.query.filter_by(category='salata', is_available=True).all()
    
    # Aktif sipariş var mı kontrol et
    active_order = Order.query.filter_by(user_id=current_user.id, status='pending').first()
    
    return render_template('user/dashboard.html', 
                         yemekler=yemekler, tatlilar=tatlilar, 
                         icecekler=icecekler, salatalar=salatalar,
                         active_order=active_order)

@user_bp.route('/menu')
@login_required
def menu():
    """Menü sayfası"""
    products = Product.query.filter_by(is_available=True).all()
    categories = ['yemek', 'tatlı', 'içecek', 'salata']
    
    return render_template('user/menu.html', products=products, categories=categories)

@user_bp.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Sepete ürün ekleme"""
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Ürün seçilmedi!'})
    
    product = Product.query.get(product_id)
    if not product or not product.is_available:
        return jsonify({'success': False, 'message': 'Ürün bulunamadı!'})
    
    # Aktif sipariş var mı kontrol et
    active_order = Order.query.filter_by(user_id=current_user.id, status='pending').first()
    
    if not active_order:
        # Yeni sipariş oluştur
        active_order = Order(user_id=current_user.id)
        db.session.add(active_order)
        db.session.flush()
    
    # Aynı ürün zaten sepette var mı kontrol et
    existing_item = OrderItem.query.filter_by(
        order_id=active_order.id, 
        product_id=product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        # Yeni sipariş kalemi ekle
        order_item = OrderItem(
            order_id=active_order.id,
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{product.name} sepete eklendi!',
        'cart_count': active_order.items.count(),
        'product_name': product.name,
        'quantity': quantity
    })

@user_bp.route('/cart')
@login_required
def cart():
    """Sepet sayfası"""
    active_order = Order.query.filter_by(user_id=current_user.id, status='pending').first()
    
    if not active_order:
        flash('Sepetinizde ürün bulunmuyor!', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Toplam tutarı hesapla
    total = active_order.calculate_total()
    
    return render_template('user/cart.html', order=active_order, total=total)

@user_bp.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    """Sepetten ürün çıkarma"""
    item = OrderItem.query.get_or_404(item_id)
    
    # Kullanıcının siparişi mi kontrol et
    if item.order.user_id != current_user.id:
        flash('Bu ürünü çıkaramazsınız!', 'error')
        return redirect(url_for('user.cart'))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Ürün sepetten çıkarıldı!', 'success')
    return redirect(url_for('user.cart'))

@user_bp.route('/update-cart', methods=['POST'])
@login_required
def update_cart():
    """Sepet güncelleme"""
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))
    
    item = OrderItem.query.get_or_404(item_id)
    
    # Kullanıcının siparişi mi kontrol et
    if item.order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bu ürünü güncelleyemezsiniz!'})
    
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Sepet güncellendi!'})

@user_bp.route('/place-order', methods=['GET', 'POST'])
@login_required
def place_order():
    """Sipariş verme"""
    active_order = Order.query.filter_by(user_id=current_user.id, status='pending').first()
    
    if not active_order or active_order.items.count() == 0:
        flash('Sepetinizde ürün bulunmuyor!', 'error')
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        table_number = request.form.get('table_number')
        
        if not table_number:
            flash('Lütfen masa numarası seçin!', 'error')
            return redirect(url_for('user.place_order'))
        
        # Masa numarasını kontrol et
        from models import Table
        table = Table.query.filter_by(table_number=int(table_number)).first()
        
        if not table:
            flash('Geçersiz masa numarası!', 'error')
            return redirect(url_for('user.place_order'))
        
        # Siparişe masa numarasını ata
        active_order.table_id = table.id
        active_order.status = 'completed'
        active_order.calculate_total()
        db.session.commit()
        
        flash('Siparişiniz oluşturuldu! 10 dakika içinde masanıza servis edilecektir.', 'success')
        return redirect(url_for('user.dashboard'))
    
    # GET isteği - masa seçimi sayfası
    from models import Table
    available_tables = Table.query.filter_by(is_occupied=False).all()
    return render_template('user/place_order.html', order=active_order, tables=available_tables)

@user_bp.route('/orders')
@login_required
def orders():
    """Sipariş durumu ve ödeme"""
    # Aktif sipariş var mı kontrol et
    active_order = Order.query.filter_by(user_id=current_user.id, status='completed').first()
    
    if not active_order:
        flash('Aktif siparişiniz bulunmuyor!', 'error')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/orders.html', order=active_order)

@user_bp.route('/checkout')
@login_required
def checkout():
    """Ödeme sayfası"""
    active_order = Order.query.filter_by(user_id=current_user.id, status='completed').first()
    
    if not active_order:
        flash('Ödenecek sipariş bulunamadı!', 'error')
        return redirect(url_for('user.dashboard'))
    
    total = active_order.calculate_total()
    return render_template('user/checkout.html', order=active_order, total=total)

@user_bp.route('/payment', methods=['POST'])
@login_required
def payment():
    """Ödemeyi kasaya yönlendirme"""
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id or order.status != 'completed':
        flash('Geçersiz sipariş!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Sipariş durumunu "payment_pending" olarak güncelle
    order.status = 'payment_pending'
    db.session.commit()
    
    flash('Ödeme kasaya yönlendirildi! Lütfen kasada ödemenizi tamamlayın.', 'success')
    return redirect(url_for('user.dashboard'))
