from flask_restful import abort

from ..models.attachments import Attachment
from ..models.users import User
from ..models.chats import Chat
from ..models.messages import Message


def handle_user_id(user_id, session):
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f'User {user_id} not found')
    return user


def handle_chat_id(chat_id, session):
    chat = session.query(Chat).get(chat_id)
    if not chat:
        abort(404, message=f'Chat {chat_id} not found')
    return chat


def handle_message_id(message_id, session):
    message = session.query(Message).get(message_id)
    if not message:
        abort(404, message=f'Message {message_id} not found')
    return message


def handle_attachment_id(attachment_id, session):
    attachment = session.query(Attachment).get(attachment_id)
    if not attachment:
        abort(404, message=f'Attachment {attachment_id} not found')
    return attachment