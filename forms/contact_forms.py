from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class ContactForm(FlaskForm):
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
    name = StringField('Adınız', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    message = TextAreaField('Yorumunuz', validators=[DataRequired(), Length(min=1, max=1000)])
    rating = IntegerField('Puan (1-5 yıldız)', 
                         validators=[Optional(), NumberRange(min=1, max=5)],
                         default=None)
    submit = SubmitField('Yorum Yap')

class ReplyForm(FlaskForm):
    reply = TextAreaField('Cevabınız', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Cevap Gönder')
