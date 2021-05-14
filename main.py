import json
import os
import time

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
from data.forms.users import LoginForm, RegisterForm, ProfileEditForm, PasswordForm
from data.models.users import User
from utils import assert_sorted_data, process_chat_form_data, save_file
from work_api import *

app = Flask(__name__, template_folder='./templates')
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['JSON_AS_ASCII'] = False
app.config['JWT_SECRET_KEY'] = 'super_secret_key'
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
        return render_template('error.html', error=error, href='/auth')
    response = make_response(render_template('index.html', chats=chats, len=len))
    response.set_cookie('token', session.get('_token'), max_age=10 ** 10)
    return response


@app.route('/chat/<int:chat_id>')
def show_chat(chat_id):
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    chat, error = get_chat(chat_id, session.get('_token'))
    if error:
        return render_template('error.html', error=error, href='/auth')
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
            return render_template('error.html', error=message, href='/'), 400
        return redirect('/')
    users, message = get_users(session.get('_token'))
    if message:
        return render_template('error.html', error=message, href='/'), 400
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
        members = ','.join([str(current_user.id)] + members.split(','))
        message = edit_chat_api(chat_id, title, members, logo, session.get('_token'))
        if isinstance(message, str):
            return render_template('error.html', error=message, href='/'), 400
        return redirect('/')
    chat, message = get_chat(chat_id, session.get('_token'))
    if message:
        return render_template('error.html', error=message, href='/'), 400
    users, message = get_users(session.get('_token'))
    if message:
        return render_template('error.html', error=message, href='/'), 400
    form.title.data = chat.get('title')
    form.users.choices = [(user.get("id"), user.get("username")) for user in users
                          if user.get('id') != current_user.id]
    form.users.assigned_choices = [user.get("username") for user in chat.get('users', [])
                                   if user.get('id') != current_user.id]
    if chat.get('logo'):
        form.logo.file.filename = chat['logo']
    return render_template('chat_form.html', form=form, submit_text='Edit')


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_user():
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    form = ProfileEditForm()
    if form.is_submitted():
        username, email, description = (form.username.data, form.email.data,
                                        form.description.data)
        logo = save_file(request.files['logo']) if request.files.get('logo') else None
        message = edit_user_api(current_user.id, session.get('_token'), username=username,
                                email=email, description=description, logo=logo)
        if isinstance(message, str):
            return render_template('error.html', error=message, href='/profile'), 400
        return redirect('/profile')
    form.logo.filename = current_user.logo
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.description.data = current_user.description
    return render_template('edit_profile.html', form=form)


@app.route('/profile/change_password', methods=['GET', 'POST'])
def change_password():
    if not current_user.is_authenticated or isinstance(current_user, AnonymousUserMixin):
        return redirect('/auth')
    form = PasswordForm()
    if form.is_submitted():
        if not current_user.check_password(form.current_password.data):
            return render_template('change_password.html',
                                   form=PasswordForm(),
                                   message='Current password is wrong'), 400
        if form.new_password.data != form.new_password_again.data:
            return render_template('change_password.html',
                                   form=PasswordForm(),
                                   message='Passwords does not match'), 400
        message = edit_user_api(current_user.id, session.get('_token'),
                                password=form.new_password.data)
        if isinstance(message, str):
            return render_template('change_password.html', form=PasswordForm(),
                                   message=message), 400
        return render_template('change_password.html', form=PasswordForm(),
                               message='Password has been changed successfully')
    return render_template('change_password.html', form=form)


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
    # При запуске на хероку:
    db_session.global_init(os.getenv('DATABASE_URL'))
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

    # При локальном запуске:
    # db_session.global_init(f"sqlite:///{os.path.join('db', 'vitamo_data.db')}?check_same_thread=False")
    # app.run()
