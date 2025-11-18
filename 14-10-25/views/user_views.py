"""
User Views - MVC View Layer
Handles all user panel related view logic
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import User, Product, Order, OrderItem, Table

class UserViews:
    """User view methods"""
    
    @staticmethod
    def render_dashboard(yemekler, tatlilar, icecekler, salatalar, active_order):
        """Render user dashboard"""
        return render_template('user/dashboard.html', 
                             yemekler=yemekler, tatlilar=tatlilar, 
                             icecekler=icecekler, salatalar=salatalar,
                             active_order=active_order)
    
    @staticmethod
    def render_menu(products, categories):
        """Render menu page"""
        return render_template('user/menu.html', products=products, categories=categories)
    
    @staticmethod
    def render_cart(order, total):
        """Render cart page"""
        return render_template('user/cart.html', order=order, total=total)
    
    @staticmethod
    def render_orders(orders):
        """Render orders page"""
        return render_template('user/orders.html', orders=orders)
    
    @staticmethod
    def render_checkout(order, total):
        """Render checkout page"""
        return render_template('user/checkout.html', order=order, total=total)
    
    @staticmethod
    def handle_cart_success(response):
        """Handle cart operation success"""
        return jsonify({
            'success': True, 
            'message': response.get('message', 'İşlem başarılı!'),
            'cart_count': response.get('cart_count', 0)
        })
    
    @staticmethod
    def handle_cart_error(message):
        """Handle cart operation error"""
        return jsonify({
            'success': False, 
            'message': message
        })
    
    @staticmethod
    def handle_order_success():
        """Handle order success"""
        flash('Siparişiniz oluşturuldu! 10 dakika içinde masanıza servis edilecektir.', 'success')
        return redirect(url_for('user.dashboard'))
    
    @staticmethod
    def handle_order_error(message):
        """Handle order error"""
        flash(message, 'error')
        return redirect(url_for('user.dashboard'))
    
    @staticmethod
    def handle_payment_success():
        """Handle payment success"""
        flash('Ödeme tamamlandı! Faturanız e-posta ile gönderildi.', 'success')
        return redirect(url_for('user.dashboard'))
    
    @staticmethod
    def handle_payment_warning():
        """Handle payment warning"""
        flash('Ödeme tamamlandı ancak fatura gönderilemedi.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    @staticmethod
    def check_user_permission():
        """Check if current user is regular user"""
        if not current_user.is_authenticated:
            flash('Bu sayfaya erişim için giriş yapmalısınız!', 'error')
            return False
        
        if not isinstance(current_user, User):
            flash('Bu sayfaya erişim yetkiniz yok!', 'error')
            return False
        
        return True
