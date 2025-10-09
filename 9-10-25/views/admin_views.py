"""
Admin Views - MVC View Layer
Handles all admin panel related view logic
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import Admin, Product, Order, OrderItem, Table, User
from forms import ProductForm, TableForm, OrderItemForm

class AdminViews:
    """Admin view methods"""
    
    @staticmethod
    def render_dashboard(tables, orders):
        """Render admin dashboard"""
        return render_template('admin/dashboard.html', tables=tables, orders=orders)
    
    @staticmethod
    def render_products(products):
        """Render products management page"""
        return render_template('admin/products.html', products=products)
    
    @staticmethod
    def render_add_product(form):
        """Render add product page"""
        return render_template('admin/add_product.html', form=form)
    
    @staticmethod
    def render_edit_product(form, product):
        """Render edit product page"""
        return render_template('admin/edit_product.html', form=form, product=product)
    
    @staticmethod
    def handle_product_success(message):
        """Handle product operation success"""
        flash(message, 'success')
        return redirect(url_for('admin.products'))
    
    @staticmethod
    def handle_product_error(message):
        """Handle product operation error"""
        flash(message, 'error')
        return None
    
    @staticmethod
    def render_tables(tables):
        """Render tables management page"""
        return render_template('admin/tables.html', tables=tables)
    
    @staticmethod
    def render_add_table(form):
        """Render add table page"""
        return render_template('admin/add_table.html', form=form)
    
    @staticmethod
    def render_edit_table(form, table):
        """Render edit table page"""
        return render_template('admin/edit_table.html', form=form, table=table)
    
    @staticmethod
    def handle_table_success(message):
        """Handle table operation success"""
        flash(message, 'success')
        return redirect(url_for('admin.tables'))
    
    @staticmethod
    def handle_table_error(message):
        """Handle table operation error"""
        flash(message, 'error')
        return None
    
    @staticmethod
    def render_table_details(table, order):
        """Render table details page"""
        return render_template('admin/table_details.html', table=table, order=order)
    
    @staticmethod
    def render_add_item_to_table(form, table):
        """Render add item to table page"""
        return render_template('admin/add_item_to_table.html', form=form, table=table)
    
    @staticmethod
    def handle_table_item_success():
        """Handle table item addition success"""
        flash('Ürün masaya eklendi!', 'success')
        return None
    
    @staticmethod
    def render_orders(orders):
        """Render orders management page"""
        return render_template('admin/orders.html', orders=orders)
    
    @staticmethod
    def render_api_table_total(total):
        """Render API table total response"""
        return jsonify({'total': total})
    
    @staticmethod
    def check_admin_permission():
        """Check if current user is admin"""
        if not current_user.is_authenticated:
            flash('Bu sayfaya erişim için giriş yapmalısınız!', 'error')
            return False
        
        if not isinstance(current_user, Admin):
            flash('Bu sayfaya erişim yetkiniz yok!', 'error')
            return False
        
        return True
