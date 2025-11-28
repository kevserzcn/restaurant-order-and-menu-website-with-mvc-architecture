"""
İletişim Formları
=================
Müşteri iletişim ve yorum formları.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class ContactForm(FlaskForm):
    """İletişim formu - sadece e-posta gönderimi için (istek, şikayet)"""
    name = StringField('Adınız', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    type = SelectField('İletişim Tipi', 
                      choices=[
                          ('request', 'İstek'),
                          ('complaint', 'Şikayet')
                      ],
                      validators=[DataRequired()])
    message = TextAreaField('Mesajınız', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Gönder')

class ReviewForm(FlaskForm):
    """Yorum formu - herkesin görebileceği yorumlar için"""
    name = StringField('Adınız', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    message = TextAreaField('Yorumunuz', validators=[DataRequired(), Length(min=1, max=1000)])
    rating = IntegerField('Puan (1-5 yıldız)', 
                         validators=[Optional(), NumberRange(min=1, max=5)],
                         default=None)
    submit = SubmitField('Yorum Yap')

class ReplyForm(FlaskForm):
    """Admin cevap formu"""
    reply = TextAreaField('Cevabınız', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Cevap Gönder')
