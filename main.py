import io
import json
import os.path
import time

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, session, Response, make_response
from flask_jwt_extended import JWTManager
from flask_login import LoginManager, login_user, logout_user, current_user, AnonymousUserMixin
from flask_restful import Api

from data import db_session
from data.api.resources.chat_resource import ChatResource, ChatListResource
from data.api.resources.message_resource import MessageResource, MessageListResource
from data.api.resources.token_resource import TokenResource
from data.api.resources.user_resource import UserResource, UserPublicListResource
from data.api.utils import get_current_user
from data.forms.chats import ChatForm
from data.forms.users import LoginForm, RegisterForm
from data.models.users import User
from utils import assert_sorted_data, generate_random_name, process_chat_form_data
from work_api import *

load_dotenv()
app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JSON_AS_ASCII'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_IDENTITY_CLAIM'] = 'user'
app.config['JWT_HEADER_NAME'] = 'authorization'
app.jwt = JWTManager(app)
api = Api(app)
api.add_resource(TokenResource, '/api/authorize')
api.add_resource(UserResource, '/api/users/<int:user_id>')
api.add_resource(UserPublicListResource, '/api/users')
api.add_resource(ChatResource, '/api/chats/<int:chat_id>')
api.add_resource(ChatListResource, '/api/chats')
api.add_resource(MessageResource, '/api/chats/<int:chat_id>/messages/<int:message_id>')
api.add_resource(MessageListResource, '/api/chats/<int:chat_id>/messages')
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
    response = make_response(render_template('main_window.html', chats=chats))
    response.set_cookie('token', session.get('_token'), max_age=10 ** 10)
    return response


@app.route('/chat/<int:chat_id>')
def show_chat(chat_id):
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    chat, error = get_chat(chat_id, session.get('_token'))
    if error:
        return render_template('error.html', error=error)
    return render_template('chat.html', chat=chat)


@app.route('/add_chat', methods=['GET', 'POST'])
def add_chat():
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    form = ChatForm()
    if form.is_submitted():
        title, members, logo = process_chat_form_data(form, request)
        message = add_chat_api(title, members, logo, session.get('_token'))
        if isinstance(message, str):
            return render_template('error.html', error=message)
        return redirect('/')
    users, message = get_users(session.get('_token'))
    if message:
        return render_template('error.html', error=message), 400
    form.users.choices = [(user.get("id"), user.get("username")) for user in users
                          if user.get('id') != current_user.id]
    return render_template('chat_form.html', form=form, submit_text='Add')


@app.route('/edit_chat/<int:chat_id>', methods=['GET', 'POST'])
def edit_chat(chat_id):
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    form = ChatForm()
    if form.is_submitted():
        title, members, logo = process_chat_form_data(form, request)
        print('dlsalda: {}'.format([str(current_user.id)] + members.split(',')))
        members = ','.join([str(current_user.id)] + members.split(','))
        print(f'members: {members}')
        message = edit_chat_api(chat_id, title, members, logo, session.get('_token'))
        if isinstance(message, str):
            return render_template('error.html', error=message), 400
        return redirect('/')
    chat, message = get_chat(chat_id, session.get('_token'))
    if message:
        return render_template('error.html', error=message), 400
    users, message = get_users(session.get('_token'))
    if message:
        return render_template('error.html', error=message), 400
    form.title.data = chat.get('title')
    form.users.choices = [(user.get("id"), user.get("username")) for user in users
                          if user.get('id') != current_user.id]
    form.users.assigned_choices = [user.get("username") for user in chat.get('users', [])
                                   if user.get('id') != current_user.id]
    if chat.get('logo'):
        form.logo.file.filename = chat['logo']
    return render_template('chat_form.html', form=form, submit_text='Edit')


@app.route('/listen')
def listen():
    token = session.get('_token')
    host_url = request.host_url

    def respond_to_client(token, host_url):
        rest_chats, error = get_chats(token, host_url=host_url)
        if error:
            return f'data: {error}\nevent: alert\n\n'
        while True:
            chats, error = get_chats(token, host_url=host_url)
            if error:
                return f'data: {error}\nevent: alert\n\n'
            if assert_sorted_data(rest_chats, chats) is not None:
                rest_chats = chats[:]
                yield f'data: {json.dumps(chats)}\nevent: new-message\n\n'
            yield 'event: online\n\n'
            time.sleep(2.5)

    return Response(respond_to_client(token, host_url), mimetype='text/event-stream')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error=error), 404


@app.errorhandler(500)
def not_found_error(error):
    return render_template('error.html', error=error), 500


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
            response = make_response(redirect('/'))
            response.delete_cookie('token')
            response.delete_cookie('opened')
            return response
        elif request.form['submit'] == 'sign up':
            message = add_new_users(register_form.username.data, register_form.email.data,
                                    register_form.password.data)
            if message:
                return render_template('authorization.html', login_form=login_form, register_form=register_form,
                                       register_message=message)
            return render_template('authorization.html', login_form=LoginForm(), register_form=RegisterForm())
    return render_template('authorization.html', login_form=login_form, register_form=register_form)


@app.route('/profile')
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    db_session.global_init(os.path.join('db', 'vitamo_data.db'))
    app.run()
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
