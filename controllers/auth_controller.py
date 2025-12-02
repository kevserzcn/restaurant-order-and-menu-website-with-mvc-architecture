from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import db
from forms import UserLoginForm, AdminLoginForm, UserRegisterForm, ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm
from utils.dual_auth import (
    login_admin, login_user_custom, logout_admin, logout_user_custom,
    is_admin_logged_in, is_user_logged_in
)

from repositories import UserRepository, AdminRepository
from validators import UserValidator
from services.otp_service import create_and_send_otp, verify_otp as verify_otp_code

auth_bp = Blueprint('auth', __name__)

user_repository = UserRepository()
admin_repository = AdminRepository()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return redirect(url_for('auth.index'))

@auth_bp.route('/user/login', methods=['GET', 'POST'])
def user_login():
    form = UserLoginForm()
    
    if form.validate_on_submit():
        user = user_repository.find_by_email(form.email.data)
        
        if user and user.check_password(form.name.data):
            login_user_custom(user)
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('E-posta veya isim hatalı!', 'error')
    
    return render_template('auth/user_login.html', form=form)

@auth_bp.route('/user/register', methods=['GET', 'POST'])
def user_register():
    form = UserRegisterForm()
    
    if form.validate_on_submit():
        is_valid, errors = UserValidator.validate_user_registration(
            email=form.email.data,
            name=form.name.data
        )
        
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/user_register.html', form=form)
        
        existing_user = user_repository.find_by_email(form.email.data)
        if existing_user:
            flash('Bu e-posta zaten kayıtlı!', 'error')
            return render_template('auth/user_register.html', form=form)
        
        user = user_repository.create_user(
            email=form.email.data,
            name=form.name.data
        )
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.user_login'))
    
    return render_template('auth/user_register.html', form=form)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = admin_repository.find_by_email(form.email.data)
        
        if admin and admin.check_password(form.password.data):
            login_admin(admin)
            flash('Admin paneline hoş geldiniz!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Email veya şifre hatalı!', 'error')
    
    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data
        
        admin = admin_repository.find_by_email(email)
        if not admin:
            flash('Bu e-posta adresi ile kayıtlı admin bulunamadı!', 'error')
            return render_template('auth/forgot_password.html', form=form)
        
        success, message = create_and_send_otp(email)
        
        if success:
            session['reset_password_email'] = email
            flash(message, 'success')
            return redirect(url_for('auth.verify_otp'))
        else:
            flash(message, 'error')
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/admin/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_password_email')
    if not email:
        flash('Lütfen önce şifre sıfırlama kodu talep edin.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = VerifyOTPForm()
    
    if form.validate_on_submit():
        code = form.code.data
        
        is_valid, message, otp = verify_otp_code(email, code)
        
        if is_valid:
            flash(message, 'success')
            session['otp_verified'] = True
            return redirect(url_for('auth.reset_password'))
        else:
            flash(message, 'error')
    
    return render_template('auth/verify_otp.html', form=form, email=email)

@auth_bp.route('/admin/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_password_email')
    otp_verified = session.get('otp_verified')
    
    if not email or not otp_verified:
        flash('Lütfen önce OTP kodunu doğrulayın.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        if new_password != confirm_password:
            flash('Şifreler eşleşmiyor!', 'error')
            return render_template('auth/reset_password.html', form=form)
        
        admin = admin_repository.find_by_email(email)
        if not admin:
            flash('Admin bulunamadı!', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        if admin.check_password(new_password):
            flash('Yeni şifre eski şifrenizle aynı olamaz! Lütfen farklı bir şifre seçin.', 'error')
            return render_template('auth/reset_password.html', form=form)
        
        admin.set_password(new_password)
        db.session.commit()
        
        session.pop('reset_password_email', None)
        session.pop('otp_verified', None)
        
        flash('Şifreniz başarıyla değiştirildi! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.admin_login'))
    
    return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/logout')
@auth_bp.route('/logout/<user_type>')
def logout(user_type=None):
    
    if user_type == 'admin':
        logout_admin()
        flash('Admin çıkışı yapıldı!', 'info')
        return redirect(url_for('auth.index'))
    elif user_type == 'user':
        logout_user_custom()
        flash('Başarıyla çıkış yaptınız!', 'info')
        return redirect(url_for('auth.index'))
    
    referer = request.referrer or ''
    
    if '/admin/' in referer:
        if is_admin_logged_in():
            logout_admin()
            flash('Admin çıkışı yapıldı!', 'info')
        else:
            flash('Zaten çıkış yapmışsınız!', 'info')
    elif '/user/' in referer:
        if is_user_logged_in():
            logout_user_custom()
            flash('Başarıyla çıkış yaptınız!', 'info')
        else:
            flash('Zaten çıkış yapmışsınız!', 'info')
    else:
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
    return render_template('index.html')

@auth_bp.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    from utils.dual_auth import get_current_user_custom
    
    if not is_user_logged_in():
        flash('Bu sayfaya erişim için kullanıcı girişi yapmalısınız!', 'error')
        return redirect(url_for('auth.user_login'))
    
    current_user = get_current_user_custom()
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        is_valid, errors = UserValidator.validate_email(email)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return render_template('user/profile.html', user=current_user)
        
        if email:
            current_user.email = email
        if name:
            current_user.name = name
        db.session.commit()
        flash('Profiliniz güncellendi.', 'success')
        return redirect(url_for('auth.user_profile'))
    return render_template('user/profile.html', user=current_user)
