from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class TableForm(FlaskForm):
    name = StringField('Masa Adı', validators=[DataRequired(), Length(min=1, max=50)])
    capacity = IntegerField('Kapasite', validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField('Kaydet')
