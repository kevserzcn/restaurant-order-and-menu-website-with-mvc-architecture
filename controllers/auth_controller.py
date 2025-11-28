"""
Kimlik Doğrulama Controller
=============================
SOLID: Single Responsibility - Sadece HTTP request handling
Business logic repository katmanında

Kullanıcı ve admin giriş/çıkış işlemlerini yöneten Blueprint.

Route'lar:
- /login: Ana giriş sayfası (index'e yönlendirir)
- /user/login: Müşteri girişi (email + isim ile)
- /user/register: Müşteri kaydı
- /admin/login: Admin girişi (email + şifre ile)
- /logout: Çıkış (admin veya user, URL parametresi ile)
- /home: Ana sayfa
- /user/profile: Kullanıcı profil sayfası

Özellikler:
- Dual authentication: Aynı tarayıcıda hem admin hem user girişi
- Session tabanlı kimlik yönetimi
- WTForms ile form validasyonu
- Flash mesajlar ile kullanıcı geri bildirimi
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from forms import UserLoginForm, AdminLoginForm, UserRegisterForm, ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm
from datetime import datetime
from utils.dual_auth import (
    login_admin, login_user_custom, logout_admin, logout_user_custom,
    is_admin_logged_in, is_user_logged_in
)

# SOLID: Dependency Injection - Repository'leri import et
from repositories import UserRepository, AdminRepository
from validators import UserValidator
from services.otp_service import create_and_send_otp, verify_otp as verify_otp_code

auth_bp = Blueprint('auth', __name__)

# Repository instance'ları oluştur
user_repository = UserRepository()
admin_repository = AdminRepository()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ana giriş sayfası - kullanıcı tipi seçimi"""
    return redirect(url_for('auth.index'))

@auth_bp.route('/user/login', methods=['GET', 'POST'])
def user_login():
    """Kullanıcı girişi - e-posta ve isim - SOLID: Repository kullanarak"""
    form = UserLoginForm()
    
    if form.validate_on_submit():
        # UserRepository ile kullanıcıyı bul
        user = user_repository.find_by_email(form.email.data)
        
        if user and user.check_password(form.name.data):
            # Yeni dual auth sistemi kullan
            login_user_custom(user)
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('E-posta veya isim hatalı!', 'error')
    
    return render_template('auth/user_login.html', form=form)

@auth_bp.route('/user/register', methods=['GET', 'POST'])
def user_register():
    """Kullanıcı kayıt - e-posta ve isim - SOLID: Repository ve Validator kullanarak"""
    form = UserRegisterForm()
    
    if form.validate_on_submit():
        # UserValidator ile doğrula
        is_valid, errors = UserValidator.validate_user_registration(
            email=form.email.data,
            name=form.name.data
        )
        
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/user_register.html', form=form)
        
        # E-posta zaten kayıtlı mı kontrol et (repository ile)
        existing_user = user_repository.find_by_email(form.email.data)
        if existing_user:
            flash('Bu e-posta zaten kayıtlı!', 'error')
            return render_template('auth/user_register.html', form=form)
        
        # UserRepository ile yeni kullanıcı oluştur
        user = user_repository.create_user(
            email=form.email.data,
            name=form.name.data
        )
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.user_login'))
    
    return render_template('auth/user_register.html', form=form)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin girişi - email ve şifre - SOLID: Repository kullanarak"""
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        # AdminRepository ile admin'i bul
        admin = admin_repository.find_by_email(form.email.data)
        
        if admin and admin.check_password(form.password.data):
            # Yeni dual auth sistemi kullan
            login_admin(admin)
            flash('Admin paneline hoş geldiniz!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Email veya şifre hatalı!', 'error')
    
    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Şifremi unuttum - OTP kodu gönderme"""
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data
        
        # Admin var mı kontrol et
        admin = admin_repository.find_by_email(email)
        if not admin:
            flash('Bu e-posta adresi ile kayıtlı admin bulunamadı!', 'error')
            return render_template('auth/forgot_password.html', form=form)
        
        # OTP kodu oluştur ve gönder
        success, message = create_and_send_otp(email)
        
        if success:
            # Email'i session'a kaydet (OTP doğrulama için)
            session['reset_password_email'] = email
            flash(message, 'success')
            return redirect(url_for('auth.verify_otp'))
        else:
            flash(message, 'error')
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/admin/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """OTP doğrulama"""
    # Email session'da var mı kontrol et
    email = session.get('reset_password_email')
    if not email:
        flash('Lütfen önce şifre sıfırlama kodu talep edin.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = VerifyOTPForm()
    
    if form.validate_on_submit():
        code = form.code.data
        
        # OTP'yi doğrula
        is_valid, message, otp = verify_otp_code(email, code)
        
        if is_valid:
            flash(message, 'success')
            # OTP doğrulandı, şifre değiştirme sayfasına yönlendir
            session['otp_verified'] = True
            return redirect(url_for('auth.reset_password'))
        else:
            flash(message, 'error')
    
    return render_template('auth/verify_otp.html', form=form, email=email)

@auth_bp.route('/admin/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Şifre sıfırlama"""
    # Email ve OTP doğrulaması kontrol et
    email = session.get('reset_password_email')
    otp_verified = session.get('otp_verified')
    
    if not email or not otp_verified:
        flash('Lütfen önce OTP kodunu doğrulayın.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        # Şifreler eşleşiyor mu kontrol et
        if new_password != confirm_password:
            flash('Şifreler eşleşmiyor!', 'error')
            return render_template('auth/reset_password.html', form=form)
        
        # Admin'i bul ve şifreyi güncelle
        admin = admin_repository.find_by_email(email)
        if not admin:
            flash('Admin bulunamadı!', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        admin.set_password(new_password)
        db.session.commit()
        
        # Session'ı temizle
        session.pop('reset_password_email', None)
        session.pop('otp_verified', None)
        
        flash('Şifreniz başarıyla değiştirildi! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.admin_login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/logout')
@auth_bp.route('/logout/<user_type>')
def logout(user_type=None):
    """Çıkış yap - hem admin hem user çıkışını destekler"""
    
    # URL parametresinden user_type belirtilmişse onu kullan
    if user_type == 'admin':
        logout_admin()
        flash('Admin çıkışı yapıldı!', 'info')
        return redirect(url_for('auth.index'))
    elif user_type == 'user':
        logout_user_custom()
        flash('Başarıyla çıkış yaptınız!', 'info')
        return redirect(url_for('auth.index'))
    
    # URL parametresi yoksa referer'dan veya session'dan anla
    referer = request.referrer or ''
    
    # Admin sayfasından geliyorsa admin çıkışı
    if '/admin/' in referer:
        if is_admin_logged_in():
            logout_admin()
            flash('Admin çıkışı yapıldı!', 'info')
        else:
            flash('Zaten çıkış yapmışsınız!', 'info')
    # User sayfasından geliyorsa user çıkışı
    elif '/user/' in referer:
        if is_user_logged_in():
            logout_user_custom()
            flash('Başarıyla çıkış yaptınız!', 'info')
        else:
            flash('Zaten çıkış yapmışsınız!', 'info')
    else:
        # Her ikisi de giriş yaptıysa, ikisini de çıkar
        logged_out = False
        if is_admin_logged_in():
            logout_admin()
            logged_out = True
        if is_user_logged_in():
            logout_user_custom()
            logged_out = True
        
        if logged_out:
            flash('Başarıyla çıkış yaptınız!', 'info')
        else:
            flash('Zaten çıkış yapmışsınız!', 'info')
    
    return redirect(url_for('auth.index'))

@auth_bp.route('/home')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@auth_bp.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    """Kullanıcı profili - SOLID: Repository kullanarak"""
    from flask import render_template
    from utils.dual_auth import get_current_user_custom, user_required
    
    if not is_user_logged_in():
        flash('Bu sayfaya erişim için kullanıcı girişi yapmalısınız!', 'error')
        return redirect(url_for('auth.user_login'))
    
    current_user = get_current_user_custom()
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        # UserValidator ile doğrula
        is_valid, errors = UserValidator.validate_email(email)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('user/profile.html', user=current_user)
        
        # UserRepository ile güncelle
        if email:
            current_user.email = email
        if name:
            current_user.name = name
        db.session.commit()
        flash('Profiliniz güncellendi.', 'success')
        return redirect(url_for('auth.user_profile'))
    return render_template('user/profile.html', user=current_user)
