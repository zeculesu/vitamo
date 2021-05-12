from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    keep_signed = BooleanField()
    submit = SubmitField('Sign In')


class ProfileEditForm(FlaskForm):
    logo = FileField('Profile Picture')
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Edit')


class PasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired()])
    new_password_again = PasswordField('New password again', validators=[DataRequired()])
    submit = SubmitField('Change')