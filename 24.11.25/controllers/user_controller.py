"""
Müşteri Paneli Controller
==========================
SOLID: Single Responsibility - Sadece HTTP request handling
Business logic service katmanında

Restoran müşterilerinin sipariş ve masa işlemlerini yöneten Blueprint.

Route'lar:
- /dashboard: Ana sayfa - kategorilere göre menü
- /menu: Menü sayfası - tüm ürünler
- /add-to-cart: Sepete ürün ekleme (AJAX)
- /cart: Sepet sayfası - masa seçimi ve sipariş tamamlama
- /remove-from-cart/<id>: Sepetten ürün çıkarma
- /update-cart: Sepet güncelleme (miktar değiştirme)
- /place-order: Sipariş verme (masa seçimi ile)
- /orders: Sipariş durumu ve geçmiş
- /checkout: Ödeme sayfası
- /payment: Ödemeyi kasaya yönlendirme
- /order/<id>/cancel: Sipariş iptal

Özellikler:
- @user_required decorator ile yetkilendirme
- Sepet yönetimi (session tabanlı)
- Masa seçimi ve rezervasyon
- Sipariş durumu takibi
- AJAX ile sepet işlemleri
- Ödeme işlemi (kasaya yönlendirme)

Sipariş Durumları:
- pending: Hazırlanıyor
- completed: Hazır, masaya servis edilecek
- payment_pending: Ödeme bekliyor
- paid: Ödeme tamamlandı
- cancelled: İptal edildi
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from extensions import db
from utils.dual_auth import user_required, get_current_user_custom
from forms import OrderItemForm
from datetime import datetime
from sqlalchemy import desc

# SOLID: Dependency Injection - Service'leri import et
from domain import ProductService, OrderService, TableService, PaymentService
from validators import OrderValidator

user_bp = Blueprint('user', __name__)

# Service instance'ları oluştur
product_service = ProductService()
order_service = OrderService()
table_service = TableService()
payment_service = PaymentService()

ACTIVE_ORDER_STATUSES = ['pending', 'completed', 'payment_pending']
PLACED_ORDER_STATUSES = ['pending', 'completed', 'payment_pending', 'paid']


def get_latest_order_for_user(user_id, statuses):
    from models import Order
    order = (Order.query
            .filter(Order.user_id == user_id, Order.status.in_(statuses))
            .order_by(desc(Order.updated_at), desc(Order.created_at), desc(Order.id))
            .first())
    
    return order

@user_bp.route('/')
@user_bp.route('/dashboard')
@user_required
def dashboard():
    """Kullanıcı ana sayfa - menü görüntüleme - SOLID: ProductService kullanarak"""
    # Kategorilere göre ürünleri getir (service üzerinden)
    yemekler = product_service.get_products_by_category('yemek', available_only=True)
    tatlilar = product_service.get_products_by_category('tatlı', available_only=True)
    icecekler = product_service.get_products_by_category('içecek', available_only=True)
    salatalar = product_service.get_products_by_category('salata', available_only=True)
    
    # Aktif sipariş var mı kontrol et (pending, completed, payment_pending)
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
    return render_template('user/dashboard.html', 
                         yemekler=yemekler, tatlilar=tatlilar, 
                         icecekler=icecekler, salatalar=salatalar,
                         active_order=active_order)

@user_bp.route('/menu')
@user_required
def menu():
    """Menü sayfası - SOLID: Service kullanarak"""
    products = product_service.get_available_products()
    categories = ['yemek', 'tatlı', 'içecek', 'salata']
    # Tüm masalar ve boş masalar listesi (service üzerinden)
    all_tables = table_service.get_all_tables()
    available_tables = table_service.get_available_tables()
    # Kullanıcının ödenmemiş mevcut siparişi (pending, completed, payment_pending)
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    return render_template('user/menu.html', products=products, categories=categories, available_tables=available_tables, all_tables=all_tables, active_order=active_order)

@user_bp.route('/add-to-cart', methods=['POST'])
@user_required
def add_to_cart():
    """Sepete ürün ekleme - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    
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
    
    # ProductService ile ürün kontrol et
    product = product_service.get_product_by_id(product_id)
    if not product or not product.is_available:
        return jsonify({'success': False, 'message': 'Ürün bulunamadı!'})
    
    # Mevcut ödenmemiş siparişi bul (pending, completed, payment_pending)
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
    print(f"DEBUG ADD_TO_CART: User ID={current_user.id}")
    print(f"DEBUG ADD_TO_CART: Active order exists={active_order is not None}")

    if active_order:
        print(f"DEBUG ADD_TO_CART: Using existing order ID={active_order.id}")
        # Eğer sipariş completed veya payment_pending durumundaysa,
        # kullanıcı aynı masasına ek ürün eklemek istiyordur, durumu pending'e çek
        if active_order.status in ['completed', 'payment_pending']:
            active_order.status = 'pending'
            active_order.updated_at = datetime.utcnow()
            db.session.commit()
    else:
        # Yeni sipariş oluştur (service üzerinden)
        active_order = order_service.create_order(
            user_id=current_user.id,
            table_id=None,
            items=[]
        )
        print(f"DEBUG ADD_TO_CART: New order created, ID={active_order.id}")
        # Yeni sipariş oluşturulduğunda db'ye kaydet
        db.session.flush()
    
    # OrderService ile ürün ekle (duplicate kontrolü service'te yapılıyor)
    try:
        order_service.add_item_to_order(
            order_id=active_order.id,
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
        print(f"DEBUG ADD_TO_CART: Item added successfully - Product ID={product_id}, Quantity={quantity}")
        # add_item_to_order içinde zaten commit yapılıyor
    except Exception as e:
        print(f"DEBUG ADD_TO_CART: Error adding item - {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})
    
    # Masa doluluk durumunu güncelle (masa atanmışsa)
    if active_order.table_id:
        from models import Table
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
@user_required
def cart():
    """Sepet sayfası - masa seçimi ve sipariş tamamlama dahil - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
    # Debug: Aktif siparişi logla
    if active_order:
        print(f"DEBUG CART: Order ID={active_order.id}, Status={active_order.status}")
        items_count = active_order.items.count()
        print(f"DEBUG CART: Items count={items_count}")
        if items_count > 0:
            for item in active_order.items.all():
                print(f"DEBUG CART: Item - Product ID={item.product_id}, Quantity={item.quantity}")
    else:
        print("DEBUG CART: No active order found!")
    
    # Eğer sipariş completed veya payment_pending durumundaysa, sepet boş demektir
    # Yeni bir sipariş başlatılmalı
    if active_order and active_order.status in ['completed', 'payment_pending']:
        # Bu sipariş zaten tamamlanmış/ödeme bekliyor, yeni sipariş için dashboard'a yönlendir
        flash('Mevcut siparişiniz tamamlandı. Yeni sipariş için ürün ekleyin.', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Sipariş yoksa veya içinde ürün yoksa
    if not active_order:
        flash('Sepetinizde ürün bulunmuyor!', 'info')
        return redirect(url_for('user.dashboard'))
    
    # Sepette ürün var mı kontrol et
    item_count = active_order.total_items()
    if item_count == 0:
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
                    # TableService ile yeni masa kontrolü
                    new_table = table_service.get_table_by_id(requested_id)
                    if not new_table:
                        flash('Geçersiz masa seçimi!', 'error')
                        return redirect(url_for('user.cart'))
                    if new_table.is_occupied and new_table.id != active_order.table_id:
                        flash('Seçtiğiniz masa şu anda dolu!', 'error')
                        return redirect(url_for('user.cart'))
                    if current_table.id != new_table.id:
                        # Eski masayı boşalt, yeni masayı işgal et
                        table_service.release_table(current_table.id)
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

            # TableService ile masa kontrolü
            selected_table = table_service.get_table_by_id(requested_id)
            if not selected_table:
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.cart'))
            if selected_table.is_occupied:
                flash('Seçtiğiniz masa şu anda dolu!', 'error')
                return redirect(url_for('user.cart'))
            active_order.table_id = selected_table.id

        # TableService ile masayı işgal et
        if selected_table and not selected_table.is_occupied:
            table_service.occupy_table(selected_table.id)

        # OrderService ile siparişi güncelle
        active_order.status = 'pending'
        active_order.calculate_total()
        active_order.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Siparişiniz mutfağa iletildi! Hazırlanıyor...', 'success')
        return redirect(url_for('user.orders', order_id=active_order.id))
    
    # GET request - sepet görüntüleme
    available_tables = table_service.get_available_tables()
    if current_table and current_table not in available_tables:
        available_tables.append(current_table)
    available_tables.sort(key=lambda t: t.name)
    
    # Toplam tutarı hesapla
    total = active_order.calculate_total()
    
    return render_template('user/cart.html', order=active_order, total=total, item_count=active_order.total_items(), 
                         tables=available_tables, current_table=current_table)

@user_bp.route('/remove-from-cart/<int:item_id>')
@user_required
def remove_from_cart(item_id):
    """Sepetten ürün çıkarma - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    
    # OrderItem'i kontrol et
    from models import OrderItem
    item = OrderItem.query.get_or_404(item_id)
    
    # Kullanıcının siparişi mi kontrol et
    if item.order.user_id != current_user.id:
        flash('Bu ürünü çıkaramazsınız!', 'error')
        return redirect(url_for('user.cart'))
    
    # OrderService ile item sil
    order_service.remove_item_from_order(item.order_id, item_id)

    flash('Ürün sepetten çıkarıldı!', 'success')
    return redirect(url_for('user.cart'))

@user_bp.route('/update-cart', methods=['POST'])
@user_required
def update_cart():
    """Sepet güncelleme - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))
    
    from models import OrderItem
    item = OrderItem.query.get_or_404(item_id)
    
    # Kullanıcının siparişi mi kontrol et
    if item.order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bu ürünü güncelleyemezsiniz!'})
    
    if quantity <= 0:
        # OrderService ile item sil
        order_service.remove_item_from_order(item.order_id, item_id)
    else:
        # Miktar güncelle
        item.quantity = quantity
        db.session.commit()
    
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    remaining = active_order.total_items() if active_order and active_order.status == 'pending' else 0

    return jsonify({'success': True, 'message': 'Sepet güncellendi!', 'remaining': remaining})

@user_bp.route('/place-order', methods=['GET', 'POST'])
@user_required
def place_order():
    """Sipariş verme - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
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
                    # TableService ile yeni masa kontrolü
                    new_table = table_service.get_table_by_id(requested_id)
                    if not new_table:
                        flash('Geçersiz masa seçimi!', 'error')
                        return redirect(url_for('user.place_order'))
                    if new_table.is_occupied and new_table.id != active_order.table_id:
                        flash('Seçtiğiniz masa şu anda dolu!', 'error')
                        return redirect(url_for('user.place_order'))
                    if current_table.id != new_table.id:
                        # Eski masayı boşalt, yeni masayı işgal et
                        table_service.release_table(current_table.id)
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

            # TableService ile masa kontrolü
            selected_table = table_service.get_table_by_id(requested_id)
            if not selected_table:
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.place_order'))
            if selected_table.is_occupied:
                flash('Seçtiğiniz masa şu anda dolu!', 'error')
                return redirect(url_for('user.place_order'))
            active_order.table_id = selected_table.id

        # TableService ile masayı işgal et
        if selected_table and not selected_table.is_occupied:
            table_service.occupy_table(selected_table.id)

        # Siparişi güncelle
        active_order.status = 'pending'
        active_order.calculate_total()
        active_order.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Siparişiniz mutfağa iletildi! Hazırlanıyor...', 'success')
        return redirect(url_for('user.orders', order_id=active_order.id))

    # GET request - boş masaları göster
    available_tables = table_service.get_available_tables()
    if current_table and current_table not in available_tables:
        available_tables.append(current_table)
    available_tables.sort(key=lambda t: t.name)

    return render_template('user/place_order.html', order=active_order, tables=available_tables, current_table=current_table)

@user_bp.route('/orders')
@user_bp.route('/orders/<int:order_id>')
@user_required
def orders(order_id=None):
    """Sipariş durumu ve ödeme - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    
    # OrderService ile kullanıcının tüm siparişlerini getir
    from models import Order
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
@user_required
def checkout():
    """Ödeme sayfası"""
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, PLACED_ORDER_STATUSES)
    
    if not active_order:
        flash('Ödenecek sipariş bulunamadı!', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Masa kontrolü - eğer masa yoksa hata ver
    if active_order.status == 'pending' and not active_order.table_id:
        flash('Lütfen önce masa seçin!', 'error')
        return redirect(url_for('user.cart'))
    
    total = active_order.calculate_total()
    return render_template('user/checkout.html', order=active_order, total=total)


@user_bp.route('/payment', methods=['POST'])
@user_required
def payment():
    """Ödemeyi kasaya yönlendirme (kullanıcı tarafından) - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')

    if not order_id:
        flash('Geçersiz istek!', 'error')
        return redirect(url_for('user.dashboard'))

    # OrderService ile siparişi getir
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('user.dashboard'))

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
@user_required
def cancel_order(order_id):
    """Kullanıcının kendi siparişini iptal etmesi - SOLID: Service kullanarak"""
    current_user = get_current_user_custom()
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('user.orders'))
    
    # Sadece sahibi iptal edebilir
    if order.user_id != current_user.id:
        flash('Bu siparişi iptal etme yetkiniz yok!', 'error')
        return redirect(url_for('user.orders'))

    # İptal edilebilir mi? Kullanıcı için izin: 'pending' ve 'payment_pending' durumlarında
    if order.status not in ['pending', 'payment_pending']:
        flash('Sadece henüz hazırlama veya ödeme aşamasındaki siparişleri iptal edebilirsiniz.', 'error')
        return redirect(url_for('user.orders', order_id=order.id))

    # OrderService ile siparişi iptal et
    order_service.cancel_order(order_id)

    # Eğer bu masada başka aktif sipariş yoksa masayı boşalt
    if order.table_id:
        from models import Order
        ACTIVE_STATUSES = ['pending', 'completed', 'payment_pending']
        other_active = (Order.query
                        .filter(Order.table_id == order.table_id,
                                Order.id != order.id,
                                Order.status.in_(ACTIVE_STATUSES))
                        .count())
        if other_active == 0:
            table_service.release_table(order.table_id)

    flash('Siparişiniz iptal edildi.', 'success')
    return redirect(url_for('user.orders'))

