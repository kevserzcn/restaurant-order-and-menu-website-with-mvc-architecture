from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class OrderItemForm(FlaskForm):
    product_id = SelectField('Ürün', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Miktar', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Ekle')
