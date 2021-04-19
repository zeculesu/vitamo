from datetime import timedelta
import os.path

from dotenv import load_dotenv

from flask import Flask, render_template, request
from flask_restful import Api
from flask_jwt_extended import JWTManager

from data import db_session
from data.api.resources.user_resource import UserResource, UserPublicListResource
from data.api.resources.chat_resource import ChatResource, ChatPublicListResource
from data.api.resources.message_resource import MessageResource, MessageListResource
from data.api.resources.token_resource import TokenResource

from work_api import add_new_users, authorize_user

load_dotenv()
app = Flask(__name__, template_folder='./templates', static_folder='./templates/static')
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
api.add_resource(ChatPublicListResource, '/api/chats')
api.add_resource(MessageResource, '/api/messages/<int:message_id>')
api.add_resource(MessageListResource, '/api/messages')


@app.route('/', methods=['POST', 'GET'])
def authorization():
    if request.method == 'GET':
        return render_template('authorization.html')
    elif request.method == 'POST':
        if request.form['submit_button'] == 'sigh_in':
            pass
            # response = authorize_user(request.form['name'], request.form['password'])
        elif request.form['submit_button'] == 'sigh_up':
            response = add_new_users(request.form['name'], request.form['email'], request.form['password'],
                                     request.form['description'])
        return response.text


if __name__ == '__main__':
    db_session.global_init(os.path.join('db', 'vitamo_data.db'))
    app.run()
