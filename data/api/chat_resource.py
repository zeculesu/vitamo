from flask import jsonify
from flask_restful import Resource, abort

from .parser import chat_parser
from .. import db_session
from ..models.chats import Chat
from .user_resource import handle_user_id


def handle_chat_id(chat_id, session):
    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f'Chat {chat_id} not found')
    return chat


class ChatResource(Resource):
    def get(self, chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        return jsonify({'chat': chat.to_dict(only=Chat.serialize_fields, chats_in_users=False)})

    def put(self, chat_id):
        session = db_session.create_session()
        chat = handle_chat_id(chat_id, session)
        args = chat_parser.parse_args()
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

    def get(self):
        session = db_session.create_session()
        chats = session.query(Chat).all()
        return jsonify({'chats': [ch.to_dict(only=Chat.serialize_fields, chats_in_users=False)
                                  for ch in chats]})

    @staticmethod
    def post():
        session = db_session.create_session()
        args = chat_parser.parse_args()
        args['users'] = [handle_user_id(user_id, session) for user_id in args['users']]
        session.add(Chat(**args))
        session.commit()
        return jsonify({'message': 'OK'})