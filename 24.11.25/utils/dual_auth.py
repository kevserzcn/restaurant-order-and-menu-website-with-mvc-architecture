"""
Dual Authentication System (İkili Kimlik Doğrulama Sistemi)
===========================================================
Aynı tarayıcıda hem admin hem user girişini destekleyen özel authentication sistemi.

Problem:
--------
Flask-Login tek bir kullanıcı tipini destekler. Aynı tarayıcıda hem admin hem 
müşteri olarak giriş yapmak mümkün değildir. İkinci giriş, birinci girişi geçersiz kılar.

Çözüm:
------
Session tabanlı özel authentication sistemi:
- Admin için: session['admin_id'], session['admin_name']
- User için: session['user_id'], session['user_name']
- Her iki session key de aynı anda aktif olabilir

Fonksiyonlar:
-------------
- login_admin(admin): Admin girişi yap
- login_user_custom(user): User girişi yap
- logout_admin(): Admin çıkışı
- logout_user_custom(): User çıkışı
- is_admin_logged_in(): Admin giriş kontrolü
- is_user_logged_in(): User giriş kontrolü
- get_current_admin(): Şu anki admin'i getir
- get_current_user_custom(): Şu anki user'ı getir

Decorator'lar:
--------------
- @admin_required: Admin yetkisi gerektirir
- @user_required: User yetkisi gerektirir

Kullanım:
---------
    # Controller'da
    from utils.dual_auth import admin_required, get_current_admin
    
    @admin_bp.route('/dashboard')
    @admin_required
    def dashboard():
        admin = get_current_admin()
        return render_template('admin/dashboard.html')
    
    # Template'de
    {% if is_admin_logged_in %}
        <p>Hoşgeldin {{ current_admin.name }}</p>
    {% endif %}

Güvenlik:
---------
- Session cookie HttpOnly
- CSRF koruması aktif
- Session timeout: 1 saat
- Her değişiklikte session.modified = True

Not: Flask-Login yerine bu sistem kullanılıyor.
"""

from flask import session, redirect, url_for, flash
from functools import wraps


def login_admin(admin):
    """Admin girişi yap - tamamen bağımsız session"""
    session['admin_id'] = admin.id
    session['admin_name'] = admin.name
    session.permanent = False
    session.modified = True


def login_user_custom(user):
    """User girişi yap - tamamen bağımsız session"""
    session['user_id'] = user.id
    session['user_name'] = user.name
    session.permanent = False
    session.modified = True


def logout_admin():
    """Admin çıkışı"""
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.modified = True


def logout_user_custom():
    """User çıkışı"""
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.modified = True


def is_admin_logged_in():
    """Admin girişli mi kontrol et"""
    return 'admin_id' in session


def is_user_logged_in():
    """User girişli mi kontrol et"""
    return 'user_id' in session


def get_current_admin():
    """Şu anki admin'i getir"""
    if is_admin_logged_in():
        from models import Admin
        from extensions import db
        return db.session.get(Admin, session.get('admin_id'))
    return None


def get_current_user_custom():
    """Şu anki user'ı getir"""
    if is_user_logged_in():
        from models import User
        from extensions import db
        return db.session.get(User, session.get('user_id'))
    return None


def admin_required(f):
    """Admin yetkisi gerektiren route decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Bu sayfaya erişim için admin girişi yapmalısınız!', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """User yetkisi gerektiren route decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_user_logged_in():
            flash('Bu sayfaya erişim için kullanıcı girişi yapmalısınız!', 'error')
            return redirect(url_for('auth.user_login'))
        return f(*args, **kwargs)
    return decorated_function
