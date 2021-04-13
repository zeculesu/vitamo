from flask import jsonify
from flask_restful import Resource, abort

from ... import db_session
from ...models.chats import Chat
from .user_resource import handle_user_id

from ..parsers.base import MethodParser
from ..parsers.chats import *

from ..utils import handle_chat_id


class ChatResource(Resource):
    @staticmethod
    def get(chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        return jsonify({'chat': chat.to_dict(only=Chat.serialize_fields, chats_in_users=False)})

    @staticmethod
    def addUser(chat_id, user_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        user = handle_user_id(user_id, session)
        if user in chat.users:
            return abort(400, message=f'User {user_id} is already in chat {chat_id}')
        chat.users.append(user)
        session.merge(chat)
        session.commit()
        return jsonify({'message': 'OK'})

    @staticmethod
    def kickUser(chat_id, user_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        user = handle_user_id(user_id, session)
        if user not in chat.users:
            return abort(400, message=f'User {user_id} is not in chat {chat_id}')
        chat.users.pop(chat.users.index(user))
        session.merge(chat)
        session.commit()
        return jsonify({'message': 'OK'})

    def post(self, chat_id):
        session = db_session.create_session()
        handle_chat_id(chat_id, session)
        method_parser = MethodParser()
        method = method_parser.parse_args()['method']
        if method is not None:
            parser = eval(f'Chat{method[0].upper() + method[1:]}Parser()')
            args = eval(f'parser.parse_args()')
            return eval(f'self.{method}(chat_id, **args)')

    @staticmethod
    def put(chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        parser = ChatAddParser()
        args = parser.parse_args()
        if args['users'] is not None:
            args['users'] = [handle_user_id(user_id, session) for user_id in args['users']]
        for key, val in filter(lambda x: x[1] is not None, args.items()):
            setattr(chat, key, val)
        session.merge(chat)
        session.commit()
        return jsonify({'message': 'OK'})

    @staticmethod
    def delete(chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        session.delete(chat)
        session.commit()
        return jsonify({'message': 'OK'})


class ChatPublicListResource(Resource):
    chat_fields = ('id', 'title', 'logo', 'users', 'messages')

    @staticmethod
    def get():
        session = db_session.create_session()
        chats = session.query(Chat).all()
        return jsonify({'chats': [ch.to_dict(only=Chat.serialize_fields, chats_in_users=False)
                                  for ch in chats]})

    @staticmethod
    def post():
        session = db_session.create_session()
        parser = ChatAddParser()
        args = parser.parse_args()
        args['users'] = [handle_user_id(user_id, session) for user_id in args['users'].split(',')]
        session.add(Chat(**args))
        session.commit()
        return jsonify({'message': 'OK'})
