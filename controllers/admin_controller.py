"""
Admin Panel Controller
======================
SOLID: Single Responsibility - Sadece HTTP request handling
Business logic service katmanında

Restoran yönetim işlemlerini sağlayan admin panel Blueprint'i.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from extensions import db
from utils.dual_auth import admin_required, get_current_admin
from forms import ProductForm, TableForm, OrderItemForm, ReplyForm
from datetime import datetime
from sqlalchemy import desc

# SOLID: Dependency Injection - Service'leri import et
from domain import ProductService, OrderService, TableService, PaymentService, ContactService
from validators import ProductValidator, OrderValidator

admin_bp = Blueprint('admin', __name__)

# Service instance'ları oluştur (Dependency Injection için)
product_service = ProductService()
order_service = OrderService()
table_service = TableService()
payment_service = PaymentService()
contact_service = ContactService()

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin ana sayfa - masa durumları"""
    tables = table_service.get_all_tables()
    pending_orders = order_service.get_pending_orders()
    payment_pending_orders = order_service.get_payment_pending_orders()
    
    return render_template('admin/dashboard.html', 
                         tables=tables, 
                         orders=pending_orders,
                         payment_pending_orders=payment_pending_orders)

@admin_bp.route('/products')
@admin_required
def products():
    """Ürün yönetimi"""
    products = product_service.get_all_products()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Ürün ekleme - SOLID: Service kullanarak"""
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
            
            # Validator ile kontrol et
            is_valid, errors = ProductValidator.validate_product(
                form.name.data,
                price,
                form.category.data
            )
            
            if not is_valid:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/add_product.html', form=form)
            
            # Resim dosyası yükleme işlemi
            image_url = None
            if form.image_file.data:
                from werkzeug.utils import secure_filename
                import os
                from flask import current_app
                
                file = form.image_file.data
                filename = secure_filename(file.filename)
                
                # Dosya ismini benzersiz yap (timestamp ekle)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                
                # Dosyayı kaydet
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # URL formatında kaydet
                image_url = f"/static/images/{filename}"
            elif form.image_url.data:
                # URL girilmişse onu kullan
                image_url = form.image_url.data
            
            # Service ile ürün oluştur
            product = product_service.create_product(
                name=form.name.data,
                price=price,
                category=form.category.data,
                description=form.description.data,
                image_url=image_url
            )
            
            flash('Ürün başarıyla eklendi!', 'success')
            return redirect(url_for('admin.products'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
    
    return render_template('admin/add_product.html', form=form)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    """Ürün düzenleme - SOLID: Service kullanarak"""
    product = product_service.get_product_by_id(id)
    
    if not product:
        flash('Ürün bulunamadı!', 'error')
        return redirect(url_for('admin.products'))
    
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
            
            # Validator ile kontrol et
            is_valid, errors = ProductValidator.validate_product(
                form.name.data,
                price,
                form.category.data
            )
            
            if not is_valid:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/edit_product.html', form=form, product=product)
            
            # Resim dosyası yükleme işlemi
            image_url = product.image_url  # Mevcut resmi koru
            if form.image_file.data:
                from werkzeug.utils import secure_filename
                import os
                from flask import current_app
                
                file = form.image_file.data
                filename = secure_filename(file.filename)
                
                # Dosya ismini benzersiz yap
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                
                # Dosyayı kaydet
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                image_url = f"/static/images/{filename}"
            elif form.image_url.data:
                # URL girilmişse onu kullan
                image_url = form.image_url.data
            
            # Service ile ürünü güncelle
            product_service.update_product(
                product_id=id,
                name=form.name.data,
                price=price,
                category=form.category.data,
                description=form.description.data,
                image_url=image_url,
                is_available=form.is_available.data
            )
            
            flash('Ürün başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.products'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
    
    return render_template('admin/edit_product.html', form=form, product=product)

@admin_bp.route('/products/delete/<int:id>')
@admin_required
def delete_product(id):
    """Ürün silme - SOLID: Service kullanarak"""
    try:
        product = product_service.get_product_by_id(id)
        if not product:
            flash('Ürün bulunamadı!', 'error')
            return redirect(url_for('admin.products'))
        
        product_service.delete_product(id)
        flash('Ürün başarıyla silindi!', 'success')
    except Exception as e:
        flash(f'Ürün silinirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/tables')
@admin_required
def tables():
    """Masa yönetimi - SOLID: Service kullanarak"""
    tables = table_service.get_all_tables()
    return render_template('admin/tables.html', tables=tables)

@admin_bp.route('/tables/add', methods=['GET', 'POST'])
@admin_required
def add_table():
    """Masa ekleme - SOLID: Service kullanarak"""
    form = TableForm()
    
    if form.validate_on_submit():
        try:
            # Service ile masa oluştur (duplicate kontrol serviste yapılıyor)
            table = table_service.create_table(
                name=form.name.data,
                capacity=form.capacity.data
            )
            flash('Masa başarıyla eklendi!', 'success')
            return redirect(url_for('admin.tables'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
    
    return render_template('admin/add_table.html', form=form)

@admin_bp.route('/tables/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_table(id):
    """Masa düzenleme - SOLID: Service kullanarak"""
    table = table_service.get_table_by_id(id)
    
    if not table:
        flash('Masa bulunamadı!', 'error')
        return redirect(url_for('admin.tables'))
    
    form = TableForm(obj=table)
    
    if form.validate_on_submit():
        try:
            table_service.update_table(
                table_id=id,
                name=form.name.data,
                capacity=form.capacity.data
            )
            flash('Masa başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.tables'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
    
    return render_template('admin/edit_table.html', form=form, table=table)

@admin_bp.route('/tables/delete/<int:id>')
@admin_required
def delete_table(id):
    """Masa silme - SOLID: Service kullanarak"""
    try:
        table = table_service.get_table_by_id(id)
        if not table:
            flash('Masa bulunamadı!', 'error')
            return redirect(url_for('admin.tables'))
        
        table_service.delete_table(id)
        flash('Masa başarıyla silindi!', 'success')
    except Exception as e:
        flash(f'Masa silinirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.tables'))

@admin_bp.route('/table/<int:table_id>')
@admin_required
def table_details(table_id):
    """Masa detayları ve hesap - SOLID: Service kullanarak"""
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        flash('Masa bulunamadı!', 'error')
        return redirect(url_for('admin.tables'))
    
    # Masanın aktif siparişini al (business logic service'te)
    current_order = table.get_current_order()
    
    return render_template('admin/table_details.html', table=table, order=current_order)

@admin_bp.route('/table/<int:table_id>/add-item', methods=['GET', 'POST'])
@admin_required
def add_item_to_table(table_id):
    """Masaya ürün ekleme (garson girişi) - SOLID: Service kullanarak"""
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        flash('Masa bulunamadı!', 'error')
        return redirect(url_for('admin.tables'))
    
    form = OrderItemForm()
    available_products = product_service.get_available_products()
    form.product_id.choices = [(p.id, f"{p.name} - {p.price}₺") for p in available_products]
    
    if form.validate_on_submit():
        try:
            # Masanın aktif siparişini bul veya oluştur
            current_order = table.get_current_order()
            
            if not current_order:
                # Yeni sipariş oluştur (admin/garson tarafından)
                current_order = order_service.create_order(
                    user_id=1,  # Geçici user_id (garson girişi)
                    table_id=table_id,
                    items=[]
                )
                # Masa dolu işaretle
                table_service.occupy_table(table_id)
            
            # Ürün bilgilerini al
            product = product_service.get_product_by_id(form.product_id.data)
            if not product:
                flash('Ürün bulunamadı!', 'error')
                return render_template('admin/add_item_to_table.html', form=form, table=table)
            
            # OrderService ile ürün ekle
            order_service.add_item_to_order(
                order_id=current_order.id,
                product_id=product.id,
                quantity=form.quantity.data,
                price=product.price
            )
            
            flash('Ürün masaya eklendi!', 'success')
            return redirect(url_for('admin.table_details', table_id=table_id))
        except Exception as e:
            flash(f'Ürün eklenirken hata oluştu: {str(e)}', 'error')
    
    return render_template('admin/add_item_to_table.html', form=form, table=table)

@admin_bp.route('/orders')
@admin_required
def orders():
    """Sipariş yönetimi - SOLID: OrderService kullanarak"""
    orders = order_service.get_all_orders()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/api/order/<int:order_id>')
@admin_required
def get_order_details(order_id):
    """Sipariş detaylarını JSON olarak döndür"""
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Sipariş bulunamadı'}), 404
    
    # Sipariş detaylarını hazırla
    items = []
    for item in order.items.all():
        items.append({
            'product_name': item.product.name,
            'quantity': item.quantity,
            'unit_price': float(item.price),
            'total': float(item.price * item.quantity)
        })
    
    order_data = {
        'id': order.id,
        'customer': {
            'name': order.customer.name if order.customer else 'Bilinmiyor',
            'email': order.customer.email if order.customer else '-'
        },
        'table': order.table.name if order.table else '-',
        'items': items,
        'total_amount': float(order.total_amount),
        'status': order.status,
        'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
        'payment': None
    }
    
    # Ödeme bilgisi varsa ekle (payments relationship lazy='dynamic' olduğu için .first() kullan)
    payment = order.payments.first()
    if payment:
        order_data['payment'] = {
            'method': payment.payment_method,
            'amount': float(payment.amount),
            'transaction_id': payment.transaction_id,
            'created_at': payment.created_at.strftime('%d.%m.%Y %H:%M')
        }
    
    return jsonify(order_data)

@admin_bp.route('/api/table/<int:table_id>/total')
@admin_required
def get_table_total(table_id):
    """Masa toplam tutarını API olarak döndür - SOLID: Service kullanarak"""
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        return jsonify({'error': 'Masa bulunamadı'}), 404
    
    total = table.get_total_amount()
    return jsonify({'total': total})

@admin_bp.route('/payment/complete/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def complete_payment(order_id):
    """Admin tarafından ödeme tamamlama - SOLID: PaymentService kullanarak"""
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if order.status == 'paid':
        flash('Bu sipariş zaten ödenmiş!', 'warning')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'cash')
        
        try:
            # PaymentService ile ödeme işle (Strategy pattern kullanılıyor)
            payment = payment_service.process_payment(
                order_id=order.id,
                payment_method=payment_method,
                transaction_id=f'ADMIN_{order.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            )
            
            if not payment:
                flash('Ödeme işlenemedi!', 'error')
                from models import User
                return render_template('admin/complete_payment.html', order=order, user=User.query.get(order.user_id))
            
            # Masa boşalt
            if order.table_id:
                table_service.release_table(order.table_id)
            
            # Kullanıcı bilgilerini al ve bildirim göster
            from models import User
            user = User.query.get(order.user_id)
            if user:
                flash(f'Ödeme tamamlandı! {user.name} isimli müşterinin ödemesi kasada tamamlandı.', 'success')
            else:
                flash('Ödeme başarıyla tamamlandı!', 'success')
            
            return redirect(url_for('admin.table_details', table_id=order.table_id))
        except Exception as e:
            flash(f'Ödeme işlenirken hata oluştu: {str(e)}', 'error')
            from models import User
            return render_template('admin/complete_payment.html', order=order, user=User.query.get(order.user_id))
    
    # GET isteği - ödeme tamamlama sayfası
    from models import User
    user = User.query.get(order.user_id)
    return render_template('admin/complete_payment.html', order=order, user=user)

@admin_bp.route('/payment/send-invoice/<int:order_id>', methods=['POST'])
@admin_required
def send_invoice(order_id):
    """Müşteriye fatura e-posta gönderme"""
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if order.status != 'paid':
        flash('Önce ödemeyi tamamlayın!', 'error')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    # Kullanıcı bilgilerini al
    from models import User
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
            # Referer'a göre yönlendir
            referer = request.referrer or ''
            if '/payments' in referer:
                return redirect(url_for('admin.payments'))
            return redirect(url_for('admin.table_details', table_id=order.table_id))

        pdf_path = generate_invoice_pdf(order)
        send_ok = send_invoice_email(recipient_email, pdf_path)
        if send_ok:
            flash('Fatura başarıyla e-posta ile gönderildi!', 'success')
        else:
            flash('E-posta gönderilemedi.', 'error')
    except Exception as e:
        flash(f'Fatura gönderilirken hata oluştu: {str(e)}', 'error')
    
    # Referer'a göre yönlendir - ödeme sayfasından geliyorsa orada kal
    referer = request.referrer or ''
    if '/payments' in referer:
        return redirect(url_for('admin.payments'))
    
    return redirect(url_for('admin.table_details', table_id=order.table_id))

@admin_bp.route('/reports')
@admin_required
def reports():
    """Raporlar sayfası - SOLID: PaymentService kullanarak"""
    from models import Payment
    from datetime import datetime
    
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
@admin_required
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
@admin_required
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
@admin_required
def cancel_payment(order_id):
    """Ödeme bekleyen siparişi iptal et - SOLID: OrderService kullanarak"""
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if order.status not in ['completed', 'payment_pending']:
        flash('Sadece "Hazır" veya "Ödeme Bekliyor" durumundaki siparişler iptal edilebilir!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        # OrderService ile siparişi iptal et
        order_service.cancel_order(order_id)
        
        # Eğer masadaki başka aktif sipariş yoksa masayı boşalt
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
        
        flash('Sipariş başarıyla iptal edildi!', 'success')
    except Exception as e:
        flash(f'Sipariş iptal edilirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/table/<int:table_id>/add-product', methods=['GET', 'POST'])
@admin_required
def add_product_to_table(table_id):
    """Masaya ürün ekleme - SOLID: Service kullanarak"""
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        flash('Masa bulunamadı!', 'error')
        return redirect(url_for('admin.tables'))
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        
        try:
            product = product_service.get_product_by_id(product_id)
            if not product:
                flash('Ürün bulunamadı!', 'error')
                return redirect(url_for('admin.table_details', table_id=table_id))
            
            # Masanın aktif siparişini bul veya oluştur
            from models import Order
            active_order = Order.query.filter_by(table_id=table_id, status='pending').first()
            
            if not active_order:
                # Yeni sipariş oluştur
                active_order = order_service.create_order(
                    user_id=None,  # Admin tarafından eklenen ürünler için user_id None
                    table_id=table_id,
                    items=[]
                )
                table_service.occupy_table(table_id)
            
            # OrderService ile ürün ekle
            order_service.add_item_to_order(
                order_id=active_order.id,
                product_id=product_id,
                quantity=quantity,
                price=product.price
            )
            
            flash(f'{product.name} ürünü masaya başarıyla eklendi!', 'success')
            return redirect(url_for('admin.table_details', table_id=table_id))
        except Exception as e:
            flash(f'Ürün eklenirken hata oluştu: {str(e)}', 'error')
            return redirect(url_for('admin.table_details', table_id=table_id))
    
    # GET isteği - ürün seçimi sayfası
    products = product_service.get_all_products()
    return render_template('admin/add_product_to_table.html', table=table, products=products)

@admin_bp.route('/init-db')
@admin_required
def init_db_route():
    """Admin panelinden basit init_db çalıştırma"""
    try:
        from init_db import init_database
        init_database()
        flash('Veritabanı başlangıç verileri yüklendi.', 'success')
    except Exception as e:
        flash(f'Init DB çalıştırılamadı: {str(e)}', 'error')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/payments')
@admin_required
def payments():
    """Ödeme yönetimi - Ödeme bekleyen siparişler - SOLID: Service kullanarak"""
    # payment_pending durumundaki siparişleri getir
    pending_payments = order_service.get_payment_pending_orders()
    
    # Ödeme tablosundan da geçmiş ödemeleri getir (varsa)
    from models import Payment
    completed_payments = Payment.query.order_by(Payment.created_at.desc()).all()
    
    return render_template('admin/payments.html', 
                         pending_payments=pending_payments,
                         completed_payments=completed_payments)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    """Admin profil sayfası"""
    admin_user = get_current_admin()
    if request.method == 'POST':
        # Ad Soyad ve E-posta güncelleme
        name = request.form.get('name')
        email = request.form.get('email')
        
        if name:
            admin_user.name = name
        if email:
            admin_user.email = email
        
        # Şifre değiştirme
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Eğer şifre alanlarından herhangi biri doldurulmuşsa
        if current_password or new_password or confirm_password:
            if not all([current_password, new_password, confirm_password]):
                flash('Şifre değiştirmek için tüm şifre alanlarını doldurun.', 'danger')
                return redirect(url_for('admin.profile'))
            
            # Mevcut şifre kontrolü
            if not admin_user.check_password(current_password):
                flash('Mevcut şifre yanlış.', 'danger')
                return redirect(url_for('admin.profile'))
            
            # Yeni şifreler eşleşiyor mu?
            if new_password != confirm_password:
                flash('Yeni şifreler eşleşmiyor.', 'danger')
                return redirect(url_for('admin.profile'))
            
            # Şifre uzunluk kontrolü
            if len(new_password) < 6:
                flash('Yeni şifre en az 6 karakter olmalıdır.', 'danger')
                return redirect(url_for('admin.profile'))
            
            # Şifreyi güncelle
            admin_user.set_password(new_password)
            flash('Profil ve şifre başarıyla güncellendi.', 'success')
        else:
            flash('Profil başarıyla güncellendi.', 'success')
        
        db.session.commit()
        
        return redirect(url_for('admin.profile'))
    
    return render_template('admin/profile.html', admin_user=admin_user)

@admin_bp.route('/reviews')
@admin_required
def reviews():
    """Admin yorumları görüntüleme sayfası"""
    # SOLID: Business logic service katmanında
    all_contacts = contact_service.get_all_contacts()
    stats = contact_service.get_statistics()
    
    return render_template('admin/reviews.html',
                         contacts=all_contacts,
                         **stats)

@admin_bp.route('/review/<int:contact_id>/reply', methods=['GET', 'POST'])
@admin_required
def reply_to_review(contact_id):
    """Yoruma cevap yazma"""
    # SOLID: Business logic service katmanında
    contact = contact_service.get_contact_by_id(contact_id)
    if not contact:
        flash('İletişim kaydı bulunamadı!', 'danger')
        return redirect(url_for('admin.reviews'))
    
    form = ReplyForm()
    current_admin = get_current_admin()
    
    if form.validate_on_submit():
        # SOLID: Service katmanı cevap yazma ve e-posta gönderme işlemlerini yönetir
        result = contact_service.reply_to_contact(
            contact_id=contact_id,
            reply_text=form.reply.data,
            admin_id=current_admin.id,
            admin_name=current_admin.name
        )
        
        if result:
            flash('Cevabınız başarıyla eklendi ve kullanıcıya e-posta gönderildi!', 'success')
        else:
            flash('Cevap eklenirken bir hata oluştu!', 'danger')
        
        return redirect(url_for('admin.reviews'))
    
    # Eğer zaten cevap varsa formu doldur
    if contact.reply and request.method == 'GET':
        form.reply.data = contact.reply
    
    return render_template('admin/reply_review.html', contact=contact, form=form)
