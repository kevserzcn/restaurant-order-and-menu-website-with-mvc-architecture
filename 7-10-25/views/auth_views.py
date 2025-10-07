"""
Authentication Views - MVC View Layer
Handles all authentication related view logic
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms import UserLoginForm, AdminLoginForm, UserRegisterForm

class AuthViews:
    """Authentication view methods"""
    
    @staticmethod
    def render_login_page():
        """Render main login page"""
        return render_template('auth/login.html')
    
    @staticmethod
    def render_user_login(form):
        """Render user login page"""
        return render_template('auth/user_login.html', form=form)
    
    @staticmethod
    def render_user_register(form):
        """Render user register page"""
        return render_template('auth/user_register.html', form=form)
    
    @staticmethod
    def render_admin_login(form):
        """Render admin login page"""
        return render_template('auth/admin_login.html', form=form)
    
    @staticmethod
    def handle_user_login_success(user):
        """Handle successful user login"""
        login_user(user)
        flash('Başarıyla giriş yaptınız!', 'success')
        return redirect(url_for('user.dashboard'))
    
    @staticmethod
    def handle_user_login_error():
        """Handle user login error"""
        flash('Telefon numarası veya isim hatalı!', 'error')
        return None
    
    @staticmethod
    def handle_user_register_success():
        """Handle successful user registration"""
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.user_login'))
    
    @staticmethod
    def handle_user_register_error():
        """Handle user registration error"""
        flash('Bu telefon numarası zaten kayıtlı!', 'error')
        return None
    
    @staticmethod
    def handle_admin_login_success(admin):
        """Handle successful admin login"""
        login_user(admin)
        flash('Admin paneline hoş geldiniz!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    @staticmethod
    def handle_admin_login_error():
        """Handle admin login error"""
        flash('Email veya şifre hatalı!', 'error')
        return None
    
    @staticmethod
    def handle_logout():
        """Handle user logout"""
        logout_user()
        flash('Başarıyla çıkış yaptınız!', 'info')
        return redirect(url_for('auth.login'))
