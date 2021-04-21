import os.path
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, session
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, login_user, logout_user, current_user, AnonymousUserMixin
from flask_restful import Api

from data import db_session
from data.models.users import User
from data.api.resources.chat_resource import ChatResource, ChatListResource
from data.api.resources.message_resource import MessageResource, MessageListResource
from data.api.resources.token_resource import TokenResource
from data.api.resources.user_resource import UserResource, UserPublicListResource
from data.api.utils import get_current_user
from data.forms.users import LoginForm, RegisterForm
from work_api import *

load_dotenv()
app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JSON_AS_ASCII'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_EXPIRES'] = timedelta(seconds=10 ** 10)
app.config['JWT_IDENTITY_CLAIM'] = 'user'
app.config['JWT_HEADER_NAME'] = 'authorization'
app.jwt = JWTManager(app)
api = Api(app)
api.add_resource(TokenResource, '/api/authorize')
api.add_resource(UserResource, '/api/users/<int:user_id>')
api.add_resource(UserPublicListResource, '/api/users')
api.add_resource(ChatResource, '/api/chats/<int:chat_id>')
api.add_resource(ChatListResource, '/api/chats')
api.add_resource(MessageResource, '/api/messages/<int:message_id>')
api.add_resource(MessageListResource, '/api/messages')
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    chats, error = get_chats(session.get('_token'))  # Список чатов
    if error:
        return render_template('error.html', error=error)
    return render_template('main_window.html', chats=chats)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error=error), 404


@app.errorhandler(500)
def not_found_error(error):
    return render_template('error.html', error=error), 500


@app.route('/chats/<int:chat_id>')
def show_chat(chat_id):
    chat, error = get_chat(chat_id, session.get('_token'))
    if error:
        return render_template('error.html', error=error)
    return render_template('chat.html', chat=chat)


@app.route('/auth', methods=['GET', 'POST'])
def authorization():
    if current_user.is_authenticated:
        logout_user()
        session.permanent = False
        session.pop('_token')
    login_form = LoginForm()
    register_form = RegisterForm()
    if request.method == 'POST':
        if request.form['submit'] == 'sign in':
            token, message = authorize_user(login_form.username.data, login_form.password.data)
            if message:
                return render_template('authorization.html', login_form=login_form, register_form=register_form,
                                       login_message=message)
            user = get_current_user(token)
            session['_token'] = token
            login_user(user, remember=login_form.keep_signed.data)
            session.permanent = login_form.keep_signed.data
            return redirect('/')
        elif request.form['submit'] == 'sign up':
            message = add_new_users(register_form.username.data, register_form.email.data,
                                    register_form.password.data)
            if message:
                return render_template('authorization.html', login_form=login_form, register_form=register_form,
                                       register_message=message)
            return render_template('authorization.html', login_form=LoginForm(), register_form=RegisterForm())
    return render_template('authorization.html', login_form=login_form, register_form=register_form)


if __name__ == '__main__':
    db_session.global_init(os.path.join('db', 'vitamo_data.db'))
    app.run()
