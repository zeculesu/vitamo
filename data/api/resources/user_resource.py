from flask import jsonify
from flask_jwt_extended import create_access_token
from flask_restful import Resource, abort

from ... import db_session
from ...models.users import User
from ..parsers.users import *
from ..parsers.base import TokenParser

from ..utils import handle_user_id, get_current_user


class UserResource(Resource):
    @staticmethod
    def get(user_id):
        session = db_session.create_session()
        get_current_user(TokenParser().parse_args()['token'], session)
        user = handle_user_id(user_id, session)
        return jsonify({'user': user.to_dict()})

    @staticmethod
    def put(user_id):
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        user = handle_user_id(user_id, session)
        if current_user.id != user.id:
            abort(401, message='You have no access to edit this User')
        parser = UserPutParser()
        args = parser.parse_args()
        if args.get('password') is not None:
            user.set_password(args.pop('password'))
        name_chars = 20
        if args.get('username') is not None and len(args['username']) > name_chars:
            abort(400, message=f'Too long username. Its length must be under {name_chars} chars')
        description_chars = 40
        if args.get('description') is not None and len(args['description']) > description_chars:
            abort(400, message=f'Too long description. Its length must be under '
                               f'{description_chars} chars')
        for key, val in filter(lambda x: x[1] is not None, args.items()):
            setattr(user, key, val)
        session.merge(user)
        session.commit()
        return jsonify({'message': 'OK'})

    @staticmethod
    def delete(user_id):
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        user = handle_user_id(user_id, session)
        if current_user.id != user.id:
            abort(401, message='You have no access to delete this User')
        session.delete(user)
        session.commit()
        return jsonify({'message': 'OK'})


class UserPublicListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        users = [user.to_dict() for user in session.query(User).all()]
        return jsonify({'users': users})

    @staticmethod
    def post():
        session = db_session.create_session()
        parser = UserAddParser()
        args = parser.parse_args()
        if session.query(User).filter(User.email == args['email']).first():
            abort(400, message=f'User with email {args["email"]} already exists')
        password = args.pop('password')
        chars = 20
        if len(args.get('username', 0)) > chars:
            abort(400, message=f'Too long username. Its length must be under {chars} chars')
        user = User(**args)
        user.set_password(password)
        session.add(user)
        session.commit()
        return jsonify({'token': create_access_token(identity=user.id)})
