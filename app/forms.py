from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, ValidationError
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

def positive_amount(form, field):
    if field.data <= 0:
        raise ValidationError('Amount must be positive')

class RechargeForm(FlaskForm):
    amount = FloatField('Recharge Amount', validators=[DataRequired(), positive_amount])
    submit = SubmitField('Recharge')
    

