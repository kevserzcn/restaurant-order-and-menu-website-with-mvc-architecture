"""
Ürün Yönetimi Formları
======================
Ürün ekleme ve düzenleme işlemleri için kullanılan formlar.

Formlar:
- ProductForm: Ürün ekleme/düzenleme (resim yükleme, kategori seçimi, fiyat)
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ProductForm(FlaskForm):
    """Ürün ekleme/düzenleme formu"""
    name = StringField('Ürün Adı', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Açıklama', validators=[Optional(), Length(max=500)])
    price = StringField('Fiyat', validators=[DataRequired()])
    category = SelectField('Kategori', 
                          choices=[('yemek', 'Yemek'), ('tatlı', 'Tatlı'), 
                                  ('içecek', 'İçecek'), ('salata', 'Salata')],
                          validators=[DataRequired()])
    is_available = BooleanField('Ürün Mevcut')
    image_file = FileField('Ürün Resmi', 
                          validators=[Optional(), 
                                    FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                                              'Sadece resim dosyaları yüklenebilir!')])
    image_url = StringField('veya Resim URL', validators=[Optional()])
    submit = SubmitField('Kaydet')
