from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, FileField
from wtforms.validators import DataRequired


class ChatForm(FlaskForm):
    title = StringField('Title')
    users = SelectMultipleField('Members', validators=[DataRequired()])
    logo = FileField('Logo')
    submit = SubmitField('Add')