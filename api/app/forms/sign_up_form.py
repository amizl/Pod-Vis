from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

class SignUpForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    institution = StringField(validators=[DataRequired()])
    name = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField(validators=[DataRequired()])
