from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from config import db
from utils.dual_auth import user_required, get_current_user_custom, is_user_logged_in
from forms import ContactForm, ReviewForm
from datetime import datetime
from sqlalchemy import desc

from services import ProductService, OrderService, TableService, ContactService
from services.email_service import send_contact_email

user_bp = Blueprint('user', __name__)

product_service = ProductService()
order_service = OrderService()
table_service = TableService()
contact_service = ContactService()

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
    yemekler = product_service.get_products_by_category('yemek', available_only=True)
    tatlilar = product_service.get_products_by_category('tatlı', available_only=True)
    icecekler = product_service.get_products_by_category('içecek', available_only=True)
    salatalar = product_service.get_products_by_category('salata', available_only=True)
    
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
    return render_template('user/dashboard.html', 
                         yemekler=yemekler, tatlilar=tatlilar, 
                         icecekler=icecekler, salatalar=salatalar,
                         active_order=active_order)

@user_bp.route('/menu')
@user_required
def menu():
    products = product_service.get_available_products()
    categories = ['yemek', 'tatlı', 'içecek', 'salata']
    all_tables = table_service.get_all_tables()
    available_tables = table_service.get_available_tables()
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    return render_template('user/menu.html', products=products, categories=categories, available_tables=available_tables, all_tables=all_tables, active_order=active_order)

@user_bp.route('/add-to-cart', methods=['POST'])
@user_required
def add_to_cart():
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
    
    product = product_service.get_product_by_id(product_id)
    if not product or not product.is_available:
        return jsonify({'success': False, 'message': 'Ürün bulunamadı!'})
    
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)

    if active_order:
        if active_order.status in ['completed', 'payment_pending']:
            active_order.status = 'pending'
            active_order.updated_at = datetime.utcnow()
            db.session.commit()
    else:
        active_order = order_service.create_order(
            user_id=current_user.id,
            table_id=None,
            items=[]
        )
        db.session.flush()
    
    try:
        order_service.add_item_to_order(
            order_id=active_order.id,
            product_id=product_id,
            quantity=quantity,
            price=product.price
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Hata: {str(e)}'})
    
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
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    
    if active_order and active_order.status in ['completed', 'payment_pending']:
        flash('Mevcut siparişiniz tamamlandı. Yeni sipariş için ürün ekleyin.', 'info')
        return redirect(url_for('user.dashboard'))
    
    if not active_order:
        flash('Sepetinizde ürün bulunmuyor!', 'info')
        return redirect(url_for('user.dashboard'))
    
    item_count = active_order.total_items()
    if item_count == 0:
        flash('Sepetinizde ürün bulunmuyor!', 'info')
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
                    return redirect(url_for('user.cart'))

                if requested_id != current_table.id:
                    new_table = table_service.get_table_by_id(requested_id)
                    if not new_table:
                        flash('Geçersiz masa seçimi!', 'error')
                        return redirect(url_for('user.cart'))
                    if new_table.is_occupied and new_table.id != active_order.table_id:
                        flash('Seçtiğiniz masa şu anda dolu!', 'error')
                        return redirect(url_for('user.cart'))
                    if current_table.id != new_table.id:
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

            selected_table = table_service.get_table_by_id(requested_id)
            if not selected_table:
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.cart'))
            if selected_table.is_occupied:
                flash('Seçtiğiniz masa şu anda dolu!', 'error')
                return redirect(url_for('user.cart'))
            active_order.table_id = selected_table.id

        if selected_table and not selected_table.is_occupied:
            table_service.occupy_table(selected_table.id)

        active_order.status = 'pending'
        active_order.calculate_total()
        active_order.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Siparişiniz mutfağa iletildi! Hazırlanıyor...', 'success')
        return redirect(url_for('user.orders', order_id=active_order.id))
    
    available_tables = table_service.get_available_tables()
    if current_table and current_table not in available_tables:
        available_tables.append(current_table)
    available_tables.sort(key=lambda t: t.name)
    
    total = active_order.calculate_total()
    
    return render_template('user/cart.html', order=active_order, total=total, item_count=active_order.total_items(), 
                         tables=available_tables, current_table=current_table)

@user_bp.route('/remove-from-cart/<int:item_id>')
@user_required
def remove_from_cart(item_id):
    current_user = get_current_user_custom()
    
    from models import OrderItem
    item = OrderItem.query.get_or_404(item_id)
    
    if item.order.user_id != current_user.id:
        flash('Bu ürünü çıkaramazsınız!', 'error')
        return redirect(url_for('user.cart'))
    
    order_service.remove_item_from_order(item.order_id, item_id)

    flash('Ürün sepetten çıkarıldı!', 'success')
    return redirect(url_for('user.cart'))

@user_bp.route('/update-cart', methods=['POST'])
@user_required
def update_cart():
    current_user = get_current_user_custom()
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))
    
    from models import OrderItem
    item = OrderItem.query.get_or_404(item_id)
    
    if item.order.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Bu ürünü güncelleyemezsiniz!'})
    
    if quantity <= 0:
        order_service.remove_item_from_order(item.order_id, item_id)
    else:
        item.quantity = quantity
        db.session.commit()
    
    active_order = get_latest_order_for_user(current_user.id, ACTIVE_ORDER_STATUSES)
    remaining = active_order.total_items() if active_order and active_order.status == 'pending' else 0

    return jsonify({'success': True, 'message': 'Sepet güncellendi!', 'remaining': remaining})

@user_bp.route('/place-order', methods=['GET', 'POST'])
@user_required
def place_order():
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
                    new_table = table_service.get_table_by_id(requested_id)
                    if not new_table:
                        flash('Geçersiz masa seçimi!', 'error')
                        return redirect(url_for('user.place_order'))
                    if new_table.is_occupied and new_table.id != active_order.table_id:
                        flash('Seçtiğiniz masa şu anda dolu!', 'error')
                        return redirect(url_for('user.place_order'))
                    if current_table.id != new_table.id:
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

            selected_table = table_service.get_table_by_id(requested_id)
            if not selected_table:
                flash('Geçersiz masa seçimi!', 'error')
                return redirect(url_for('user.place_order'))
            if selected_table.is_occupied:
                flash('Seçtiğiniz masa şu anda dolu!', 'error')
                return redirect(url_for('user.place_order'))
            active_order.table_id = selected_table.id

        if selected_table and not selected_table.is_occupied:
            table_service.occupy_table(selected_table.id)

        active_order.status = 'pending'
        active_order.calculate_total()
        active_order.updated_at = datetime.utcnow()
        db.session.commit()

        flash('Siparişiniz mutfağa iletildi! Hazırlanıyor...', 'success')
        return redirect(url_for('user.orders', order_id=active_order.id))

    available_tables = table_service.get_available_tables()
    if current_table and current_table not in available_tables:
        available_tables.append(current_table)
    available_tables.sort(key=lambda t: t.name)

    return render_template('user/place_order.html', order=active_order, tables=available_tables, current_table=current_table)

@user_bp.route('/orders')
@user_bp.route('/orders/<int:order_id>')
@user_required
def orders(order_id=None):
    current_user = get_current_user_custom()
    
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
        active_order = next((o for o in order_history if o.status in PLACED_ORDER_STATUSES and o.status != 'cancelled'), None)
        if not active_order:
            active_order = next((o for o in order_history if o.status != 'cancelled'), order_history[0])

    if active_order.total_amount == 0 and active_order.items.count() > 0:
        active_order.calculate_total()
        db.session.commit()

    return render_template('user/orders.html', order=active_order, orders=order_history)

@user_bp.route('/checkout')
@user_required
def checkout():
    current_user = get_current_user_custom()
    active_order = get_latest_order_for_user(current_user.id, PLACED_ORDER_STATUSES)
    
    if not active_order:
        flash('Ödenecek sipariş bulunamadı!', 'error')
        return redirect(url_for('user.dashboard'))
    
    if active_order.status == 'pending' and not active_order.table_id:
        flash('Lütfen önce masa seçin!', 'error')
        return redirect(url_for('user.cart'))
    
    total = active_order.calculate_total()
    return render_template('user/checkout.html', order=active_order, total=total)


@user_bp.route('/payment', methods=['POST'])
@user_required
def payment():
    current_user = get_current_user_custom()
    order_id = request.form.get('order_id')
    payment_method = request.form.get('payment_method')

    if not order_id:
        flash('Geçersiz istek!', 'error')
        return redirect(url_for('user.dashboard'))

    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('user.dashboard'))

    if order.user_id != current_user.id:
        flash('Geçersiz sipariş!', 'error')
        return redirect(url_for('user.dashboard'))

    if order.status not in ['pending', 'completed']:
        flash('Bu sipariş için ödeme yapılamaz!', 'error')
        return redirect(url_for('user.dashboard'))

    success = order_service.request_payment(order_id)
    
    if not success:
        flash('Ödeme yönlendirme işlemi başarısız oldu!', 'error')
        return redirect(url_for('user.dashboard'))

    flash('Ödeme kasaya yönlendirildi! Lütfen kasada ödemenizi tamamlayın.', 'success')
    return redirect(url_for('user.dashboard'))


@user_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
@user_required
def cancel_order(order_id):
    current_user = get_current_user_custom()
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('user.orders'))
    
    if order.user_id != current_user.id:
        flash('Bu siparişi iptal etme yetkiniz yok!', 'error')
        return redirect(url_for('user.orders'))

    if order.status not in ['pending', 'payment_pending']:
        flash('Sadece henüz hazırlama veya ödeme aşamasındaki siparişleri iptal edebilirsiniz.', 'error')
        return redirect(url_for('user.orders', order_id=order.id))

    order_service.cancel_order(order_id)

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


@user_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    current_user = None
    
    if is_user_logged_in():
        current_user = get_current_user_custom()
        if request.method == 'GET':
            form.name.data = current_user.name
            form.email.data = current_user.email
    
    if form.validate_on_submit():
        contact_service.create_contact(
            name=form.name.data,
            email=form.email.data,
            contact_type=form.type.data,
            message=form.message.data,
            rating=None,
            user_id=current_user.id if current_user else None,
            is_visible=False
        )
        
        send_contact_email(
            contact_name=form.name.data,
            contact_email=form.email.data,
            contact_type=form.type.data,
            message=form.message.data,
            rating=None
        )
        
        flash('Mesajınız başarıyla gönderildi! Teşekkür ederiz.', 'success')
        return redirect(url_for('user.contact'))
    
    return render_template('user/contact.html', form=form, user=current_user)


@user_bp.route('/reviews', methods=['GET', 'POST'])
def reviews():
    form = ReviewForm()
    current_user = None
    
    if is_user_logged_in():
        current_user = get_current_user_custom()
        if request.method == 'GET':
            form.name.data = current_user.name
            form.email.data = current_user.email
    
    if form.validate_on_submit():
        rating = request.form.get('rating')
        rating = int(rating) if rating and rating.isdigit() else None
        
        contact_service.create_contact(
            name=form.name.data,
            email=form.email.data,
            contact_type='comment',
            message=form.message.data,
            rating=rating,
            user_id=current_user.id if current_user else None,
            is_visible=True
        )
        
        flash('Yorumunuz başarıyla eklendi! Teşekkür ederiz.', 'success')
        return redirect(url_for('user.reviews'))
    
    visible_contacts = contact_service.get_visible_comments()
    
    ratings = [c.rating for c in visible_contacts if c.rating]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    rating_counts = {i: 0 for i in range(1, 6)}
    for contact in visible_contacts:
        if contact.rating:
            rating_counts[contact.rating] += 1
    
    return render_template('user/reviews.html', 
                         form=form,
                         contacts=visible_contacts,
                         avg_rating=round(avg_rating, 1),
                         rating_counts=rating_counts,
                         total_reviews=len(visible_contacts),
                         user=current_user)

