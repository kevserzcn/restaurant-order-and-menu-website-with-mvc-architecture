"""
Masa Yönetimi Formları
======================
Masa ekleme ve düzenleme işlemleri için kullanılan formlar.

Formlar:
- TableForm: Masa ekleme/düzenleme (kapasite, garson adı)
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class TableForm(FlaskForm):
    """Masa ekleme/düzenleme formu"""
    name = StringField('Masa Adı', validators=[DataRequired(), Length(min=1, max=50)])
    capacity = IntegerField('Kapasite', validators=[DataRequired(), NumberRange(min=1, max=20)])
    waiter_name = StringField('Garson Adı', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Kaydet')
