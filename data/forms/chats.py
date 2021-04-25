from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, FileField


class ChatAddForm(FlaskForm):
    title = StringField('Title')
    users = SelectMultipleField('Members')
    logo = FileField('Logo')
    submit = SubmitField('Add')