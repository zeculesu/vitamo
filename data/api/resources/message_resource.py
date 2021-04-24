from flask import jsonify
from flask_restful import Resource, abort

from ..parsers.base import TokenParser
from ... import db_session
from ...models.chats import Chat
from ...models.messages import Message
from ..parsers.messages import MessageAddParser, MessagePutParser
from ..utils import handle_message_id, handle_attachment_id, handle_chat_id, get_current_user


class MessageResource(Resource):
    @staticmethod
    def get(chat_id, message_id):
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        handle_chat_id(chat_id, session)
        message = handle_message_id(message_id, session)
        print(f'message.chat: {message.chat}')
        print('\n'.join([f'message.chat_id: {message.chat.id}',
                         f'chat_id: {chat_id}',
                         f'current_user.id: {current_user.id}',
                         f'message.viewable_for: {[user.id for user in message.viewable_for]}']))
        if message.chat.id != chat_id or current_user.id not in [user.id for user in
                                                                 message.viewable_for]:
            abort(403, message='You have no access to this Message')
        return jsonify({'message': message.to_dict()})

    @staticmethod
    def put(chat_id, message_id):
        session = db_session.create_session()
        message = handle_message_id(message_id, session)
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        handle_chat_id(chat_id, session)
        if chat_id not in [ch.id for ch in current_user.chats]:
            abort(403, message='You have no access to this Chat')
        if (current_user.id != message.sender or current_user.id
                not in [user.id for user in message.viewable_for]):
            abort(403, message='You have no access to this Message')
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
    def delete(chat_id, message_id):
        session = db_session.create_session()
        message = handle_message_id(message_id, session)
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        handle_chat_id(chat_id, session)
        if chat_id not in [ch.id for ch in current_user.chats]:
            abort(403, message='You have no access to this Chat')
        if (current_user.id != message.sender or current_user.id
                not in [user.id for user in message.viewable_for]):
            abort(403, message='You have no access to this Message')
        session.delete(message)
        session.commit()
        return jsonify({'message': 'OK'})


class MessageListResource(Resource):
    @staticmethod
    def get(chat_id):
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        if chat_id not in [ch.id for ch in current_user.chats]:
            abort(403, message='You have no access to the messages of this Chat')
        messages = session.query(Message).all()
        return jsonify({'messages': [msg.to_dict() for msg in messages
                                     if current_user.id in [user.id for user in msg.viewable_for]]})

    @staticmethod
    def post(chat_id):
        session = db_session.create_session()
        current_user = get_current_user(TokenParser().parse_args()['token'], session)
        chat = handle_chat_id(chat_id, session)
        if chat_id not in [ch.id for ch in current_user.chats]:
            abort(403, message='You have no access to this Chat')
        parser = MessageAddParser()
        args = parser.parse_args()
        if not args['text'] and not args['attachments']:
            abort(400, message=f'Empty message')
        if args['attachments'] is None:
            args['attachments'] = list()
        for msg in session.query(Message).filter((Chat.id == chat.id) & (Message.is_read == 0)):
            msg.is_read = True
            session.merge(msg)
            session.commit()
        args['chat_id'] = chat_id
        args['sender'] = current_user.id
        message = Message(**args)
        message.viewable_for = chat.users[:]
        session.add(message)
        session.commit()
        chat.messages.append(message)
        session.merge(chat)
        session.commit()
        return jsonify({'message': 'OK'})
