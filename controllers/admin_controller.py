from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from config import db
from utils.dual_auth import admin_required, get_current_admin
from forms import ProductForm, TableForm, OrderItemForm, ReplyForm
from datetime import datetime
from services import ProductService, OrderService, TableService, PaymentService, ContactService
from validators import ProductValidator

admin_bp = Blueprint('admin', __name__)

product_service = ProductService()
order_service = OrderService()
table_service = TableService()
payment_service = PaymentService()
contact_service = ContactService()

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():

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
   
    products = product_service.get_all_products()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
   
    form = ProductForm()
    
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
            
            
            is_valid, errors = ProductValidator.validate_product(
                form.name.data,
                price,
                form.category.data
            )
            
            if not is_valid:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/add_product.html', form=form)
            
           
            image_url = None
            if form.image_file.data:
                from werkzeug.utils import secure_filename
                import os
                from flask import current_app
                
                file = form.image_file.data
                filename = secure_filename(file.filename)
                

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                
                
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
               
                image_url = f"/static/images/{filename}"
            elif form.image_url.data:
                image_url = form.image_url.data
            
         
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
    
    product = product_service.get_product_by_id(id)
    
    if not product:
        flash('Ürün bulunamadı!', 'error')
        return redirect(url_for('admin.products'))
    
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
            
           
            is_valid, errors = ProductValidator.validate_product(
                form.name.data,
                price,
                form.category.data
            )
            
            if not is_valid:
                for error in errors:
                    flash(error, 'error')
                return render_template('admin/edit_product.html', form=form, product=product)
            
            
            image_url = product.image_url  
            if form.image_file.data:
                from werkzeug.utils import secure_filename
                import os
                from flask import current_app
                
                file = form.image_file.data
                filename = secure_filename(file.filename)
                
               
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                
             
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                image_url = f"/static/images/{filename}"
            elif form.image_url.data:
                
                image_url = form.image_url.data
            
            
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
    
    try:
        product = product_service.get_product_by_id(id)
        if not product:
            flash('Ürün bulunamadı!', 'error')
            return redirect(url_for('admin.products'))
        
       
        from models.order import OrderItem
        order_items_count = OrderItem.query.filter_by(product_id=id).count()
        
        
        success = product_service.delete_product(id)
        if success:
            if order_items_count > 0:
                flash('Ürün sipariş geçmişinde bulunduğu için devre dışı bırakıldı!', 'warning')
            else:
                flash('Ürün başarıyla silindi!', 'success')
        else:
            flash('Ürün silinirken hata oluştu!', 'error')
    except Exception as e:
        flash(f'Ürün silinirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.products'))

@admin_bp.route('/tables')
@admin_required
def tables():
    tables = table_service.get_all_tables()
    return render_template('admin/tables.html', tables=tables)

@admin_bp.route('/tables/add', methods=['GET', 'POST'])
@admin_required
def add_table():
    form = TableForm()
    
    if form.validate_on_submit():
        try:
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
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        flash('Masa bulunamadı!', 'error')
        return redirect(url_for('admin.tables'))
    
    current_order = table.get_current_order()
    
    return render_template('admin/table_details.html', table=table, order=current_order)

@admin_bp.route('/table/<int:table_id>/add-item', methods=['GET', 'POST'])
@admin_required
def add_item_to_table(table_id):
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        flash('Masa bulunamadı!', 'error')
        return redirect(url_for('admin.tables'))
    
    form = OrderItemForm()
    available_products = product_service.get_available_products()
    form.product_id.choices = [(p.id, f"{p.name} - {p.price}₺") for p in available_products]
    
    if form.validate_on_submit():
        try:
            current_order = table.get_current_order()
            
            if not current_order:
                current_order = order_service.create_order(
                    user_id=1,  
                    table_id=table_id,
                    items=[]
                )
                table_service.occupy_table(table_id)
            
            product = product_service.get_product_by_id(form.product_id.data)
            if not product:
                flash('Ürün bulunamadı!', 'error')
                return render_template('admin/add_item_to_table.html', form=form, table=table)
            
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
    orders = order_service.get_all_orders()
    return render_template('admin/orders.html', orders=orders)

@admin_bp.route('/api/order/<int:order_id>')
@admin_required
def get_order_details(order_id):
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        return jsonify({'error': 'Sipariş bulunamadı'}), 404
    
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
    table = table_service.get_table_by_id(table_id)
    
    if not table:
        return jsonify({'error': 'Masa bulunamadı'}), 404
    
    total = table.get_total_amount()
    return jsonify({'total': total})

@admin_bp.route('/payment/complete/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def complete_payment(order_id):
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
            payment = payment_service.process_payment(
                order_id=order.id,
                payment_method=payment_method,
                transaction_id=f'ADMIN_{order.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            )
            
            if not payment:
                flash('Ödeme işlenemedi!', 'error')
                from models import User
                return render_template('admin/complete_payment.html', order=order, user=User.query.get(order.user_id))
            
            if order.table_id:
                table_service.release_table(order.table_id)
            
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
    
    from models import User
    user = User.query.get(order.user_id)
    return render_template('admin/complete_payment.html', order=order, user=user)

@admin_bp.route('/orders/<int:order_id>/send_invoice', methods=['POST'])
@admin_required
def send_invoice(order_id):
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if order.status != 'paid':
        flash('Önce ödemeyi tamamlayın!', 'error')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    from models import User
    user = User.query.get(order.user_id)
    if not user:
        flash('Kullanıcı bulunamadı!', 'error')
        return redirect(url_for('admin.table_details', table_id=order.table_id))
    
    try:
        from services.pdf_service import generate_invoice_pdf
        from services.email_service import send_invoice_email
        
        recipient_email = request.form.get('invoice_email') or user.email if hasattr(user, 'email') else None
        if not recipient_email:
            flash('E-posta adresi gerekli!', 'error')
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
    
    referer = request.referrer or ''
    if '/payments' in referer:
        return redirect(url_for('admin.payments'))
    
    return redirect(url_for('admin.table_details', table_id=order.table_id))

@admin_bp.route('/reports')
@admin_required
def reports():
    from models import Payment
    from datetime import datetime
    
    today = datetime.now().date()
    today_payments = Payment.query.filter(
        db.func.date(Payment.created_at) == today
    ).all()
    
    month_start = datetime.now().replace(day=1).date()
    monthly_payments = Payment.query.filter(
        db.func.date(Payment.created_at) >= month_start
    ).all()
    
    total_revenue = sum(p.amount for p in Payment.query.filter_by(status='completed').all())
    today_revenue = sum(p.amount for p in today_payments if p.status == 'completed')
    monthly_revenue = sum(p.amount for p in monthly_payments if p.status == 'completed')
    
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
    from services.pdf_service import generate_report_pdf
    from models import Payment
    from datetime import datetime
    
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
    from services.excel_service import generate_report_excel
    from models import Payment
    from datetime import datetime
    
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
    order = order_service.get_order_by_id(order_id)
    
    if not order:
        flash('Sipariş bulunamadı!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if order.status not in ['completed', 'payment_pending']:
        flash('Sadece "Hazır" veya "Ödeme Bekliyor" durumundaki siparişler iptal edilebilir!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
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
        
        flash('Sipariş başarıyla iptal edildi!', 'success')
    except Exception as e:
        flash(f'Sipariş iptal edilirken hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/init-db')
@admin_required
def init_db_route():
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
    pending_payments = order_service.get_payment_pending_orders()
    
    from models import Payment
    completed_payments = Payment.query.order_by(Payment.created_at.desc()).all()
    
    return render_template('admin/payments.html', 
                         pending_payments=pending_payments,
                         completed_payments=completed_payments)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    admin_user = get_current_admin()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        if name:
            admin_user.name = name
        if email:
            admin_user.email = email
        
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password or new_password or confirm_password:
            if not all([current_password, new_password, confirm_password]):
                flash('Şifre değiştirmek için tüm şifre alanlarını doldurun.', 'danger')
                return redirect(url_for('admin.profile'))
            
            if not admin_user.check_password(current_password):
                flash('Mevcut şifre yanlış.', 'danger')
                return redirect(url_for('admin.profile'))
            
            if new_password != confirm_password:
                flash('Yeni şifreler eşleşmiyor.', 'danger')
                return redirect(url_for('admin.profile'))
            
            if len(new_password) < 6:
                flash('Yeni şifre en az 6 karakter olmalıdır.', 'danger')
                return redirect(url_for('admin.profile'))
            
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

    all_contacts = contact_service.get_all_contacts()
    stats = contact_service.get_statistics()
    
    return render_template('admin/reviews.html',
                         contacts=all_contacts,
                         **stats)

@admin_bp.route('/review/<int:contact_id>/reply', methods=['GET', 'POST'])
@admin_required
def reply_to_review(contact_id):

    contact = contact_service.get_contact_by_id(contact_id)
    if not contact:
        flash('İletişim kaydı bulunamadı!', 'danger')
        return redirect(url_for('admin.reviews'))
    
    form = ReplyForm()
    current_admin = get_current_admin()
    
    if form.validate_on_submit():
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
    
    if contact.reply and request.method == 'GET':
        form.reply.data = contact.reply
    
    return render_template('admin/reply_review.html', contact=contact, form=form)
