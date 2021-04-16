from flask import jsonify
from flask_restful import Resource, abort

from ... import db_session
from ...models.chats import Chat
from ...models.messages import Message
from ..parsers.messages import MessageAddParser, MessagePutParser
from ..utils import handle_message_id, handle_attachment_id, handle_chat_id


class MessageResource(Resource):
    @staticmethod
    def get(message_id):
        session = db_session.create_session()
        message = handle_message_id(message_id, session)
        return jsonify({'message': message.to_dict()})

    @staticmethod
    def put(message_id):
        session = db_session.create_session()
        message = handle_message_id(message_id, session)
        parser = MessagePutParser()
        args = parser.parse_args()
        if args['chat_id'] is not None:
            args.pop('chat_id')
        if args['attachments'] is not None:
            args['attachments'] = [handle_attachment_id(attach_id) for attach_id
                                   in args['attachments'].split(',')]
        for key, val in filter(lambda x: x[1] is not None, args.items()):
            if message.text != args['text'] and not message.is_edited:
                message.is_edited = True
            setattr(message, key, val)
        session.merge(message)
        session.commit()
        return jsonify({'message': 'OK'})

    @staticmethod
    def delete(message_id):
        session = db_session.create_session()
        message = handle_message_id(message_id, session)
        session.delete(message)
        session.commit()
        return jsonify({'message': 'OK'})


class MessageListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        messages = session.query(Message).all()
        return jsonify({'messages': [msg.to_dict() for msg in messages]})

    @staticmethod
    def post():
        session = db_session.create_session()
        parser = MessageAddParser()
        args = parser.parse_args()
        if not args['text'] and not args['attachments']:
            abort(400, message=f'Empty message')
        if args['attachments'] is None:
            args['attachments'] = list()
        chat = handle_chat_id(args['chat_id'], session)
        for msg in session.query(Message).filter((Chat.id == chat.id) & (Message.is_read == 0)):
            msg.is_read = True
            session.merge(msg)
            session.commit()
        message = Message(**args)
        session.add(message)
        session.commit()
        chat.messages.append(message)
        session.merge(chat)
        session.commit()
        return jsonify({'message': 'OK'})
