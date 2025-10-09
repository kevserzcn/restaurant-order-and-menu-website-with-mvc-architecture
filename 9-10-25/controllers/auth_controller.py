from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Admin
from forms import UserLoginForm, AdminLoginForm, UserRegisterForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ana giriş sayfası - kullanıcı tipi seçimi"""
    return redirect(url_for('auth.index'))

@auth_bp.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """Kullanıcı girişi - e-posta ve isim"""
    form = UserLoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.name.data):
            login_user(user)
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('E-posta veya isim hatalı!', 'error')
    
    return render_template('auth/user_login.html', form=form)

@auth_bp.route('/user/register', methods=['GET', 'POST'])
def user_register():
    """Kullanıcı kayıt - e-posta ve isim"""
    form = UserRegisterForm()
    
    if form.validate_on_submit():
        # E-posta zaten kayıtlı mı kontrol et
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Bu e-posta zaten kayıtlı!', 'error')
            return render_template('auth/user_register.html', form=form)
        
        # Yeni kullanıcı oluştur
        user = User(
            email=form.email.data,
            name=form.name.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.user_login'))
    
    return render_template('auth/user_register.html', form=form)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin girişi - email ve şifre"""
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash('Admin paneline hoş geldiniz!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Email veya şifre hatalı!', 'error')
    
    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Çıkış yap"""
    logout_user()
    flash('Başarıyla çıkış yaptınız!', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/home')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@auth_bp.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    from flask import render_template
    if not isinstance(current_user, User):
        flash('Bu sayfaya erişim yetkiniz yok!', 'error')
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        if email:
            current_user.email = email
        if name:
            current_user.name = name
        db.session.commit()
        flash('Profiliniz güncellendi.', 'success')
        return redirect(url_for('auth.user_profile'))
    return render_template('user/profile.html', user=current_user)
