import os.path

from flask import Flask
from flask_restful import Api

from data import db_session
from data.api.user_resource import UserResource, UserPublicListResource

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
api = Api(app)
api.add_resource(UserResource, '/api/users/<int:user_id>')
api.add_resource(UserPublicListResource, '/api/users')

if __name__ == '__main__':
    db_session.global_init(os.path.join('db', 'vitamo_data.db'))
    app.run()
