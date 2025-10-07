from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Admin, Product, Order, OrderItem, Table, User
from forms import ProductForm, TableForm, OrderItemForm
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def check_admin():
    """Admin yetkisi kontrolü"""
    if not current_user.is_authenticated:
        flash('Bu sayfaya erişim için giriş yapmalısınız!', 'error')
        return redirect(url_for('auth.login'))
    
    # Admin kontrolü - current_user'ın Admin sınıfından olup olmadığını kontrol et
    from models import Admin
    # Admin tablosunda bu kullanıcı var mı kontrol et
    admin_user = Admin.query.get(current_user.id)
    if not admin_user:
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin ana sayfa - masa durumları"""
    tables = Table.query.all()
    pending_orders = Order.query.filter_by(status='pending').all()
    payment_pending_orders = Order.query.filter_by(status='payment_pending').all()
    
    return render_template('admin/dashboard.html', 
                         tables=tables, 
                         orders=pending_orders,
                         payment_pending_orders=payment_pending_orders)

@admin_bp.route('/products')
@login_required
def products():
    """Ürün yönetimi"""
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Ürün ekleme"""
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
            product = Product(
                name=form.name.data,
                description=form.description.data,
                price=price,
                category=form.category.data,
                image_url=form.image_url.data
            )
            db.session.add(product)
            db.session.commit()
            flash('Ürün başarıyla eklendi!', 'success')
            return redirect(url_for('admin.products'))
        except ValueError:
            flash('Geçerli bir fiyat giriniz!', 'error')
    
    return render_template('admin/add_product.html', form=form)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Ürün düzenleme"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        try:
            product.name = form.name.data
            product.description = form.description.data
            product.price = float(form.price.data)
            product.category = form.category.data
            product.image_url = form.image_url.data
            db.session.commit()
            flash('Ürün başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.products'))
        except ValueError:
            flash('Geçerli bir fiyat giriniz!', 'error')
    
    return render_template('admin/edit_product.html', form=form, product=product)

@admin_bp.route('/products/delete/<int:id>')
@login_required
def delete_product(id):
    """Ürün silme"""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Ürün başarıyla silindi!', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/tables')
@login_required
def tables():
    """Masa yönetimi"""
    tables = Table.query.all()
    return render_template('admin/tables.html', tables=tables)

@admin_bp.route('/tables/add', methods=['GET', 'POST'])
@login_required
def add_table():
    """Masa ekleme"""
    form = TableForm()
    
    if form.validate_on_submit():
        # Masa numarası zaten var mı kontrol et
        existing_table = Table.query.filter_by(table_number=form.table_number.data).first()
        if existing_table:
            flash('Bu masa numarası zaten mevcut!', 'error')
            return render_template('admin/add_table.html', form=form)
        
        table = Table(
            table_number=form.table_number.data,
            capacity=form.capacity.data,
            waiter_name=form.waiter_name.data
        )
        db.session.add(table)
        db.session.commit()
        flash('Masa başarıyla eklendi!', 'success')
        return redirect(url_for('admin.tables'))
    
    return render_template('admin/add_table.html', form=form)

@admin_bp.route('/tables/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_table(id):
    """Masa düzenleme"""
    table = Table.query.get_or_404(id)
    form = TableForm(obj=table)
    
    if form.validate_on_submit():
        table.table_number = form.table_number.data
        table.capacity = form.capacity.data
        table.waiter_name = form.waiter_name.data
        db.session.commit()
        flash('Masa başarıyla güncellendi!', 'success')
        return redirect(url_for('admin.tables'))
    
    return render_template('admin/edit_table.html', form=form, table=table)

@admin_bp.route('/tables/delete/<int:id>')
@login_required
def delete_table(id):
    """Masa silme"""
    table = Table.query.get_or_404(id)
    db.session.delete(table)
    db.session.commit()
    flash('Masa başarıyla silindi!', 'success')
    return redirect(url_for('admin.tables'))

@admin_bp.route('/table/<int:table_id>')
@login_required
def table_details(table_id):
    """Masa detayları ve hesap"""
    table = Table.query.get_or_404(table_id)
    current_order = table.get_current_order()
    
    return render_template('admin/table_details.html', table=table, order=current_order)

@admin_bp.route('/table/<int:table_id>/add-item', methods=['GET', 'POST'])
@login_required
def add_item_to_table(table_id):
    """Masaya ürün ekleme (garson girişi)"""
    table = Table.query.get_or_404(table_id)
    form = OrderItemForm()
    form.product_id.choices = [(p.id, f"{p.name} - {p.price}₺") for p in Product.query.filter_by(is_available=True).all()]
    
    if form.validate_on_submit():
        # Mevcut sipariş var mı kontrol et
        current_order = table.get_current_order()
        if not current_order:
            # Yeni sipariş oluştur
            current_order = Order(user_id=1, table_id=table_id)  # Geçici user_id
            db.session.add(current_order)
            db.session.flush()
        
        # Ürün bilgilerini al
        product = Product.query.get(form.product_id.data)
        
        # Sipariş kalemi ekle
        order_item = OrderItem(
            order_id=current_order.id,
            product_id=product.id,
            quantity=form.quantity.data,
            price=product.price
        )
        db.session.add(order_item)
        db.session.commit()
        
        flash('Ürün masaya eklendi!', 'success')
        return redirect(url_for('admin.table_details', table_id=table_id))
    
    return render_template('admin/add_item_to_table.html', form=form, table=table)

@admin_bp.route('/orders')
@login_required
def orders():
    """Sipariş yönetimi"""
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/api/table/<int:table_id>/total')
@login_required
def get_table_total(table_id):
    """Masa toplam tutarını API olarak döndür"""
    table = Table.query.get_or_404(table_id)
    total = table.get_total_amount()
    return jsonify({'total': total})

@admin_bp.route('/payment/complete/<int:order_id>', methods=['GET', 'POST'])
@login_required
def complete_payment(order_id):
    """Admin tarafından ödeme tamamlama"""
    order = Order.query.get_or_404(order_id)
    
    if order.status == 'paid':
        flash('Bu sipariş zaten ödenmiş!', 'warning')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'cash')
        
        # Ödeme kaydı oluştur
        from models import Payment
        payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            payment_method=payment_method,
            status='completed',
            transaction_id=f'ADMIN_{order.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )
        db.session.add(payment)
        
        # Sipariş durumunu güncelle
        order.status = 'paid'
        db.session.commit()
        
        # Kullanıcı bilgilerini al ve bildirim göster
        user = User.query.get(order.user_id)
        if user:
            flash(f'Ödeme tamamlandı! {user.name} isimli müşterinin ödemesi kasada tamamlandı.', 'success')
        else:
            flash('Ödeme başarıyla tamamlandı!', 'success')
        
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    # GET isteği - ödeme tamamlama sayfası
    user = User.query.get(order.user_id)
    return render_template('admin/complete_payment.html', order=order, user=user)

@admin_bp.route('/payment/send-invoice/<int:order_id>', methods=['POST'])
@login_required
def send_invoice(order_id):
    """Müşteriye fatura e-posta gönderme"""
    order = Order.query.get_or_404(order_id)
    
    if order.status != 'paid':
        flash('Önce ödemeyi tamamlayın!', 'error')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    # Kullanıcı bilgilerini al
    user = User.query.get(order.user_id)
    if not user:
        flash('Kullanıcı bulunamadı!', 'error')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    try:
        # PDF fatura oluştur ve e-posta gönder
        from services.pdf_service import generate_invoice_pdf
        from services.email_service import send_invoice_email
        
        recipient_email = request.form.get('invoice_email') or user.email if hasattr(user, 'email') else None
        if not recipient_email:
            flash('E-posta adresi gerekli!', 'error')
            return redirect(url_for('admin.table_details', table_id=order.table_id))

        pdf_path = generate_invoice_pdf(order)
        send_ok = send_invoice_email(recipient_email, pdf_path)
        if send_ok:
            flash('Fatura başarıyla e-posta ile gönderildi!', 'success')
        else:
            flash('E-posta gönderilemedi.', 'error')
    except Exception as e:
        flash(f'Fatura gönderilirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.table_details', table_id=order.table_id))

@admin_bp.route('/reports')
@login_required
def reports():
    """Raporlar sayfası"""
    from models import Payment, Order
    from datetime import datetime, timedelta
    
    # Bugünkü ödemeler
    today = datetime.now().date()
    today_payments = Payment.query.filter(
        db.func.date(Payment.created_at) == today
    ).all()
    
    # Bu ayki ödemeler
    month_start = datetime.now().replace(day=1).date()
    monthly_payments = Payment.query.filter(
        db.func.date(Payment.created_at) >= month_start
    ).all()
    
    # Toplam istatistikler
    total_revenue = sum(p.amount for p in Payment.query.filter_by(status='completed').all())
    today_revenue = sum(p.amount for p in today_payments if p.status == 'completed')
    monthly_revenue = sum(p.amount for p in monthly_payments if p.status == 'completed')
    
    # Ödeme yöntemleri
    payment_methods = db.session.query(
        Payment.payment_method,
        db.func.count(Payment.id).label('count'),
        db.func.sum(Payment.amount).label('total')
    ).filter_by(status='completed').group_by(Payment.payment_method).all()
    
    return render_template('admin/reports.html', 
                         today_payments=today_payments,
                         monthly_payments=monthly_payments,
                         total_revenue=total_revenue,
                         today_revenue=today_revenue,
                         monthly_revenue=monthly_revenue,
                         payment_methods=payment_methods)

@admin_bp.route('/reports/export/pdf')
@login_required
def export_pdf():
    """PDF rapor export"""
    from services.pdf_service import generate_report_pdf
    from models import Payment
    from datetime import datetime
    
    # Tüm ödemeleri al
    payments = Payment.query.filter_by(status='completed').order_by(Payment.created_at.desc()).all()
    
    try:
        pdf_path = generate_report_pdf(payments)
        return send_file(pdf_path, as_attachment=True, download_name=f'rapor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    except Exception as e:
        flash(f'PDF oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('admin.reports'))

@admin_bp.route('/reports/export/excel')
@login_required
def export_excel():
    """Excel rapor export"""
    from services.excel_service import generate_report_excel
    from models import Payment
    from datetime import datetime
    
    # Tüm ödemeleri al
    payments = Payment.query.filter_by(status='completed').order_by(Payment.created_at.desc()).all()
    
    try:
        excel_path = generate_report_excel(payments)
        return send_file(excel_path, as_attachment=True, download_name=f'rapor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    except Exception as e:
        flash(f'Excel oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('admin.reports'))

@admin_bp.route('/payment/cancel/<int:order_id>')
@login_required
def cancel_payment(order_id):
    """Ödeme bekleyen siparişi iptal et"""
    order = Order.query.get_or_404(order_id)
    
    if order.status != 'payment_pending':
        flash('Bu sipariş ödeme bekliyor durumunda değil!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Sipariş durumunu iptal olarak güncelle
    order.status = 'cancelled'
    db.session.commit()
    
    flash('Sipariş başarıyla iptal edildi!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/table/<int:table_id>/add-product', methods=['GET', 'POST'])
@login_required
def add_product_to_table(table_id):
    """Masaya ürün ekleme"""
    table = Table.query.get_or_404(table_id)
    from models import Product, Order, OrderItem
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        
        product = Product.query.get_or_404(product_id)
        
        # Masanın aktif siparişini bul veya oluştur
        active_order = Order.query.filter_by(table_id=table_id, status='pending').first()
        
        if not active_order:
            # Yeni sipariş oluştur
            active_order = Order(
                user_id=None,  # Admin tarafından eklenen ürünler için user_id None
                table_id=table_id
            )
            db.session.add(active_order)
            db.session.flush()  # ID'yi almak için
        
        # Ürünü siparişe ekle
        existing_item = OrderItem.query.filter_by(
            order_id=active_order.id,
            product_id=product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = OrderItem(
                order_id=active_order.id,
                product_id=product_id,
                quantity=quantity,
                price=product.price
            )
            db.session.add(new_item)
        
        db.session.commit()
        flash(f'{product.name} ürünü masaya başarıyla eklendi!', 'success')
        return redirect(url_for('admin.table_details', table_id=table_id))
    
    # GET isteği - ürün seçimi sayfası
    products = Product.query.all()
    return render_template('admin/add_product_to_table.html', table=table, products=products)

@admin_bp.route('/payments')
@login_required
def payments():
    """Ödeme yönetimi"""
    from models import Payment
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments)

@admin_bp.route('/profile')
@login_required
def profile():
    """Admin profil sayfası"""
    admin_user = Admin.query.get_or_404(current_user.id)
    return render_template('admin/profile.html', admin_user=admin_user)
