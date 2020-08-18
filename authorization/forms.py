from wtforms import StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    email = StringField('Email Address')
    password = PasswordField('Password')
    remember = SubmitField()

class RegisterForm(FlaskForm):
    name = StringField('Your name')
    email = StringField('Email Address')
    password = PasswordField('Password')
    
