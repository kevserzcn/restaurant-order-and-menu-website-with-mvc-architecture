"""
Kimlik Doğrulama Formları
=========================
Giriş ve kayıt işlemleri için kullanılan formlar.

Formlar:
- UserLoginForm: Müşteri girişi (email + isim)
- UserRegisterForm: Müşteri kaydı (email + isim)
- AdminLoginForm: Admin girişi (email + şifre)
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class UserLoginForm(FlaskForm):
    """Müşteri giriş formu - email ve isim ile"""
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    name = StringField('İsim', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Giriş Yap')


class UserRegisterForm(FlaskForm):
    """Müşteri kayıt formu - email ve isim ile"""
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    name = StringField('İsim', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Kayıt Ol')


class AdminLoginForm(FlaskForm):
    """Admin giriş formu - email ve şifre ile"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')
