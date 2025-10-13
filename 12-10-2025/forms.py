from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
import re

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

class ProductForm(FlaskForm):
    name = StringField('Ürün Adı', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Açıklama', validators=[Optional(), Length(max=500)])
    price = StringField('Fiyat', validators=[DataRequired()])
    category = SelectField('Kategori', 
                          choices=[('yemek', 'Yemek'), ('tatlı', 'Tatlı'), 
                                  ('içecek', 'İçecek'), ('salata', 'Salata')],
                          validators=[DataRequired()])
    image_url = StringField('Resim URL', validators=[Optional()])
    submit = SubmitField('Kaydet')

class TableForm(FlaskForm):
    table_number = IntegerField('Masa Numarası', validators=[DataRequired(), NumberRange(min=1, max=100)])
    capacity = IntegerField('Kapasite', validators=[DataRequired(), NumberRange(min=1, max=20)])
    waiter_name = StringField('Garson Adı', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Kaydet')

class OrderItemForm(FlaskForm):
    product_id = SelectField('Ürün', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Miktar', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Ekle')
