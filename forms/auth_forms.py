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


class ForgotPasswordForm(FlaskForm):
    """Şifremi unuttum formu"""
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    submit = SubmitField('Kod Gönder')


class VerifyOTPForm(FlaskForm):
    """OTP doğrulama formu"""
    code = StringField('Doğrulama Kodu', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Doğrula')


class ResetPasswordForm(FlaskForm):
    """Şifre sıfırlama formu"""
    new_password = PasswordField('Yeni Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifre Tekrar', validators=[DataRequired()])
    submit = SubmitField('Şifreyi Değiştir')
