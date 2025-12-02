from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class UserLoginForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    name = StringField('İsim', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Giriş Yap')


class UserRegisterForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    name = StringField('İsim', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Kayıt Ol')


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    submit = SubmitField('Giriş Yap')


class ForgotPasswordForm(FlaskForm):
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    submit = SubmitField('Kod Gönder')


class VerifyOTPForm(FlaskForm):
    code = StringField('Doğrulama Kodu', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Doğrula')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Yeni Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifre Tekrar', validators=[DataRequired()])
    submit = SubmitField('Şifreyi Değiştir')
