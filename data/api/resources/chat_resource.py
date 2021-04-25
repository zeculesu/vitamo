from flask import jsonify
from flask_restful import Resource, abort

from ..parsers.base import MethodParser, TokenParser
from ..parsers.chats import *
from ..utils import get_current_user, handle_user_id, handle_chat_id
from ... import db_session
from ...models.chats import Chat


class ChatResource(Resource):
    @staticmethod
    def get(chat_id):
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        chat = handle_chat_id(chat_id, session)
        if chat.id not in [ch.id for ch in current_user.chats]:
            abort(401, message='You have no access to this Chat')
        return jsonify({'chat': chat.to_dict()})

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
        chat = handle_chat_id(chat_id, session)
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        if chat not in current_user.chats:
            abort(401, message='You have no access to this Chat')
        method_parser = MethodParser()
        method = method_parser.parse_args()['method']
        if method is not None:
            try:
                parser = eval(f'Chat{method[0].upper() + method[1:]}Parser()')
            except NameError:
                abort(404, message='Unknown method was provided')
            else:
                args = parser.parse_args()
                return eval(f'self.{method}(chat_id, **args)')

    @staticmethod
    def put(chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        if chat.id not in [ch.id for ch in current_user.chats]:
            abort(401, message='You have no access to this Chat')
        parser = ChatPutParser()
        args = parser.parse_args()
        if args['users'] is not None:
            args['users'] = [handle_user_id(user_id, session) for user_id in args['users'].split(',')]
        for key, val in filter(lambda x: x[1] is not None, args.items()):
            setattr(chat, key, val)
        if not chat.title:
            users_names = [user.username for user in chat.users]
            if len(users_names) > 3:
                users_names = users_names[:3]
            chat.title = ', '.join(users_names)
        session.merge(chat)
        session.commit()
        return jsonify({'message': 'OK'})

    @staticmethod
    def delete(chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        if chat.id not in [ch.id for ch in current_user.chats]:
            abort(401, message='You have no access to this Chat')
        session.delete(chat)
        session.commit()
        return jsonify({'message': 'OK'})


class ChatListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        chats = session.query(Chat).all()
        return jsonify({'chats': [ch.to_dict() for ch in chats if current_user.id in
                                  [user.id for user in ch.users]]})

    @staticmethod
    def post():
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        parser = ChatAddParser()
        args = parser.parse_args()
        users = [str(current_user.id)] + [user for user in args.pop('users').split(',')
                                          if user != str(current_user.id)]
        chat = Chat(**args)
        chat.users = [handle_user_id(user_id, session) for user_id in users]
        if not chat.title:
            users_names = [user.username for user in chat.users]
            if len(users_names) > 3:
                users_names = users_names[:3]
            chat.title = ', '.join(users_names)
        session.add(chat)
        session.commit()
        return jsonify({'message': 'OK'})
