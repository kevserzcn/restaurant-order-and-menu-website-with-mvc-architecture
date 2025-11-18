from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from extensions import db
from models import User, Product, Order, OrderItem, Table
from forms import OrderItemForm
from datetime import datetime
from sqlalchemy import desc

user_bp = Blueprint('user', __name__)

ACTIVE_ORDER_STATUSES = ['pending', 'completed', 'payment_pending']
PLACED_ORDER_STATUSES = ['completed', 'payment_pending', 'paid']


def get_latest_order_for_user(user_id, statuses):
    return (Order.query
            .filter(Order.user_id == user_id, Order.status.in_(statuses))
            .order_by(desc(Order.updated_at), desc(Order.created_at), desc(Order.id))
            .first())

@user_bp.before_request
def check_user():
    """Kullanıcı yetkisi kontrolü"""
    from models import Admin
    # Admin değilse User olmalı (veya giriş yapmamış)
    if not current_user.is_authenticated:
        flash('Bu sayfaya erişim için giriş yapmalısınız!', 'error')
        return redirect(url_for('auth.index'))
    
    # Admin ise user sayfasına erişemez
    if isinstance(current_user, Admin):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.index'))

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
    
    # Aktif sipariş var mı kontrol et (pending, completed, payment_pending)
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
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
    # Tüm masalar ve boş masalar listesi
    all_tables = Table.query.all()
    available_tables = [t for t in all_tables if not t.is_occupied]
    # Kullanıcının ödenmemiş mevcut siparişi (pending, completed, payment_pending)
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    return render_template('user/menu.html', products=products, categories=categories, available_tables=available_tables, all_tables=all_tables, active_order=active_order)

@user_bp.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Sepete ürün ekleme"""
    try:
        product_id = int(request.form.get('product_id'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Geçersiz ürün!'}), 400

    try:
        quantity = int(request.form.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        quantity = 1
    table_id = request.form.get('table_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Ürün seçilmedi!'})
    
    product = Product.query.get(product_id)
    if not product or not product.is_available:
        return jsonify({'success': False, 'message': 'Ürün bulunamadı!'})
    
    # Mevcut ödenmemiş siparişi bul (pending, completed, payment_pending)
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)

    if active_order:
        # Eğer sipariş completed veya payment_pending durumundaysa,
        # kullanıcı aynı masasına ek ürün eklemek istiyordur, durumu pending'e çek
        if active_order.status in ['completed', 'payment_pending']:
            active_order.status = 'pending'
            active_order.updated_at = datetime.utcnow()
    else:
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
    # Masa doluluk durumunu güncelle (masa atanmışsa)
    if active_order.table_id:
        table = Table.query.get(active_order.table_id)
        if table and not table.is_occupied:
            table.is_occupied = True
            db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'{product.name} Sepete Eklendi! ♥',
    'cart_count': active_order.total_items(),
        'product_name': product.name,
        'quantity': quantity
    })

@user_bp.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    """Sepet sayfası - masa seçimi ve sipariş tamamlama dahil"""
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
    # Eğer sipariş completed veya payment_pending durumundaysa, sepet boş demektir
    # Yeni bir sipariş başlatılmalı
    if active_order and active_order.status in ['completed', 'payment_pending']:
        # Bu sipariş zaten tamamlanmış/ödeme bekliyor, yeni sipariş için dashboard'a yönlendir
        flash('Mevcut siparişiniz tamamlandı. Yeni sipariş için ürün ekleyin.', 'info')
        return redirect(url_for('user.dashboard'))
    
    if not active_order or active_order.total_items() == 0:
        flash('Sepetinizde ürün bulunmuyor!', 'info')
        return redirect(url_for('user.dashboard'))
    
    current_table = active_order.table if active_order.table_id else None

    # POST request - sipariş tamamlama
    if request.method == 'POST':
        table_id = request.form.get('table_id')
        selected_table = None

        if current_table:
            selected_table = current_table
            if table_id:
                try:
                    requested_id = int(table_id)
                except (TypeError, ValueError):
                    flash('Geçersiz masa seçimi!', 'error')
                    return redirect(url_for('user.cart'))

                if requested_id != current_table.id:
                    new_table = Table.query.filter_by(id=requested_id).first()
                    if not new_table:
                        flash('Geçersiz masa seçimi!', 'error')
                        return redirect(url_for('user.cart'))
                    if new_table.is_occupied and new_table.id != active_order.table_id:
                        flash('Seçtiğiniz masa şu anda dolu!', 'error')
                        return redirect(url_for('user.cart'))
                    if current_table.id != new_table.id:
                        current_table.is_occupied = False
                        selected_table = new_table
                        active_order.table_id = new_table.id
        else:
            if not table_id:
                flash('Lütfen masa seçin!', 'error')
                return redirect(url_for('user.cart'))
            try:
                requested_id = int(table_id)
            except (TypeError, ValueError):
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.cart'))

            selected_table = Table.query.filter_by(id=requested_id).first()
            if not selected_table:
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.cart'))
            if selected_table.is_occupied:
                flash('Seçtiğiniz masa şu anda dolu!', 'error')
                return redirect(url_for('user.cart'))
            active_order.table_id = selected_table.id

        if selected_table and not selected_table.is_occupied:
            selected_table.is_occupied = True

        active_order.status = 'completed'
        active_order.calculate_total()
        active_order.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Siparişiniz oluşturuldu! 10 dakika içinde masanıza servis edilecektir.', 'success')
        return redirect(url_for('user.orders', order_id=active_order.id))
    
    # GET request - sepet görüntüleme
    available_tables = Table.query.filter_by(is_occupied=False).all()
    if current_table and current_table not in available_tables:
        available_tables.append(current_table)
    available_tables.sort(key=lambda t: t.name)
    
    # Toplam tutarı hesapla
    total = active_order.calculate_total()
    
    return render_template('user/cart.html', order=active_order, total=total, item_count=active_order.total_items(), 
                         tables=available_tables, current_table=current_table)

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
    
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    remaining = active_order.total_items() if active_order and active_order.status == 'pending' else 0

    return jsonify({'success': True, 'message': 'Sepet güncellendi!', 'remaining': remaining})

@user_bp.route('/place-order', methods=['GET', 'POST'])
@login_required
def place_order():
    """Sipariş verme"""
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)

    if not active_order or active_order.items.count() == 0:
        flash('Sepetinizde ürün bulunmuyor!', 'error')
        return redirect(url_for('user.dashboard'))

    current_table = active_order.table if active_order.table_id else None

    if request.method == 'POST':
        table_id = request.form.get('table_id')
        selected_table = None

        if current_table:
            selected_table = current_table
            if table_id:
                try:
                    requested_id = int(table_id)
                except (TypeError, ValueError):
                    flash('Geçersiz masa seçimi!', 'error')
                    return redirect(url_for('user.place_order'))

                if requested_id != current_table.id:
                    new_table = Table.query.filter_by(id=requested_id).first()
                    if not new_table:
                        flash('Geçersiz masa seçimi!', 'error')
                        return redirect(url_for('user.place_order'))
                    if new_table.is_occupied and new_table.id != active_order.table_id:
                        flash('Seçtiğiniz masa şu anda dolu!', 'error')
                        return redirect(url_for('user.place_order'))
                    if current_table.id != new_table.id:
                        current_table.is_occupied = False
                        selected_table = new_table
                        active_order.table_id = new_table.id
        else:
            if not table_id:
                flash('Lütfen masa seçin!', 'error')
                return redirect(url_for('user.place_order'))
            try:
                requested_id = int(table_id)
            except (TypeError, ValueError):
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.place_order'))

            selected_table = Table.query.filter_by(id=requested_id).first()
            if not selected_table:
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.place_order'))
            if selected_table.is_occupied:
                flash('Seçtiğiniz masa şu anda dolu!', 'error')
                return redirect(url_for('user.place_order'))
            active_order.table_id = selected_table.id

        if selected_table and not selected_table.is_occupied:
            selected_table.is_occupied = True

        active_order.status = 'completed'
        active_order.calculate_total()
        active_order.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Siparişiniz oluşturuldu! 10 dakika içinde masanıza servis edilecektir.', 'success')
        return redirect(url_for('user.orders', order_id=active_order.id))

    available_tables = Table.query.filter_by(is_occupied=False).all()
    if current_table and current_table not in available_tables:
        available_tables.append(current_table)
    available_tables.sort(key=lambda t: t.name)

    return render_template('user/place_order.html', order=active_order, tables=available_tables, current_table=current_table)

@user_bp.route('/orders')
@user_bp.route('/orders/<int:order_id>')
@login_required
def orders(order_id=None):
    """Sipariş durumu ve ödeme"""
    order_history = (Order.query
                     .filter(Order.user_id == current_user.id)
                     .order_by(desc(Order.updated_at), desc(Order.created_at), desc(Order.id))
                     .all())

    if not order_history:
        flash('Henüz geçmiş siparişiniz bulunmuyor!', 'info')
        return redirect(url_for('user.dashboard'))

    if order_id:
        active_order = next((o for o in order_history if o.id == order_id), None)
        if not active_order:
            flash('Bu siparişe erişim yetkiniz yok veya sipariş bulunamadı.', 'error')
            return redirect(url_for('user.orders'))
    else:
        # Choose the most recent non-cancelled placed order as active, otherwise fall back to first available
        active_order = next((o for o in order_history if o.status in PLACED_ORDER_STATUSES and o.status != 'cancelled'), None)
        if not active_order:
            # fall back to first non-cancelled order, or the very first order in history
            active_order = next((o for o in order_history if o.status != 'cancelled'), order_history[0])

    if active_order.total_amount == 0 and active_order.items.count() > 0:
        active_order.calculate_total()
        db.session.commit()

    return render_template('user/orders.html', order=active_order, orders=order_history)

@user_bp.route('/checkout')
@login_required
def checkout():
    """Ödeme sayfası"""
    active_order = get_latest_order_for_user(current_user.id, PLACED_ORDER_STATUSES)
    
    if not active_order:
        flash('Ödenecek sipariş bulunamadı!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Eğer sipariş hala pending durumundaysa, completed yap
    if active_order.status == 'pending':
        # Masa kontrolü - eğer masa yoksa hata ver
        if not active_order.table_id:
            flash('Lütfen önce masa seçin!', 'error')
            return redirect(url_for('user.cart'))
        active_order.status = 'completed'
        active_order.updated_at = datetime.utcnow()
        db.session.commit()
    
    total = active_order.calculate_total()
    return render_template('user/checkout.html', order=active_order, total=total)


@user_bp.route('/payment', methods=['POST'])
@login_required
def payment():
    """Ödemeyi kasaya yönlendirme (kullanıcı tarafından)"""
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')

    if not order_id:
        flash('Geçersiz istek!', 'error')
        return redirect(url_for('user.dashboard'))

    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash('Geçersiz sipariş!', 'error')
        return redirect(url_for('user.dashboard'))

    # Sadece pending veya completed durumları için ödeme kabul et
    if order.status not in ['pending', 'completed']:
        flash('Bu sipariş için ödeme yapılamaz!', 'error')
        return redirect(url_for('user.dashboard'))

    # Sipariş durumunu ödeme bekliyor olarak güncelle
    order.status = 'payment_pending'
    order.updated_at = datetime.utcnow()
    db.session.commit()

    flash('Ödeme kasaya yönlendirildi! Lütfen kasada ödemenizi tamamlayın.', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Kullanıcının kendi siparişini iptal etmesi (sadece payment'e taşınmamış ve hazır değilse)"""
    order = Order.query.get_or_404(order_id)
    # Sadece sahibi iptal edebilir
    if order.user_id != current_user.id:
        flash('Bu siparişi iptal etme yetkiniz yok!', 'error')
        return redirect(url_for('user.orders'))

    # İptal edilebilir mi? Kullanıcı için izin: 'pending' ve 'payment_pending' durumlarında
    if order.status not in ['pending', 'payment_pending']:
        flash('Sadece henüz hazırlama veya ödeme aşamasındaki siparişleri iptal edebilirsiniz.', 'error')
        return redirect(url_for('user.orders', order_id=order.id))

    order.status = 'cancelled'

    # Eğer bu masada başka aktif sipariş yoksa masayı boşalt
    if order.table_id:
        ACTIVE_STATUSES = ['pending', 'completed', 'payment_pending']
        other_active = (Order.query
                        .filter(Order.table_id == order.table_id,
                                Order.id != order.id,
                                Order.status.in_(ACTIVE_STATUSES))
                        .count())
        if other_active == 0:
            table = Table.query.get(order.table_id)
            if table:
                table.is_occupied = False

    db.session.commit()
    flash('Siparişiniz iptal edildi.', 'success')
    return redirect(url_for('user.orders'))
    return redirect(url_for('user.dashboard'))

