from flask import jsonify
from flask_jwt_extended import create_access_token
from flask_restful import Resource, abort

from ... import db_session
from ..parsers.token import TokenGetParser
from ...models.users import User


class TokenResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        parser = TokenGetParser()
        args = parser.parse_args()
        user = session.query(User).filter(User.username == args['username']).first()
        if not user:
            abort(404, message=f'User with username {args["username"]} not found')
        if not user.check_password(args['password']):
            abort(400, message=f'Invalid username or password')
        return jsonify({'token': create_access_token(identity=user.id)})
