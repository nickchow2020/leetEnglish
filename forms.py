from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SelectField,TextAreaField
from wtforms.validators import InputRequired,Optional,Email,DataRequired


class Login_form(FlaskForm):
    """Sign in Form"""
    username = StringField("Username",validators=[InputRequired()])
    password = PasswordField("Password",validators=[InputRequired()])

class MessageForm(FlaskForm):
    """Form for adding/editing messages."""
    text = TextAreaField('text', validators=[DataRequired()])