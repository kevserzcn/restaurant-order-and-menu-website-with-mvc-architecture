from flask import session, redirect, url_for, flash
from functools import wraps


def login_admin(admin):
    session['admin_id'] = admin.id
    session['admin_name'] = admin.name
    session.permanent = False
    session.modified = True


def login_user_custom(user):
    session['user_id'] = user.id
    session['user_name'] = user.name
    session.permanent = False
    session.modified = True


def logout_admin():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.modified = True


def logout_user_custom():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.modified = True


def is_admin_logged_in():
    return 'admin_id' in session


def is_user_logged_in():
    return 'user_id' in session


def get_current_admin():
    if is_admin_logged_in():
        from models import Admin
        from config import db
        return db.session.get(Admin, session.get('admin_id'))
    return None


def get_current_user_custom():
    if is_user_logged_in():
        from models import User
        from config import db
        return db.session.get(User, session.get('user_id'))
    return None


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Bu sayfaya erişim için admin girişi yapmalısınız!', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_user_logged_in():
            flash('Bu sayfaya erişim için kullanıcı girişi yapmalısınız!', 'error')
            return redirect(url_for('auth.user_login'))
        return f(*args, **kwargs)
    return decorated_function
