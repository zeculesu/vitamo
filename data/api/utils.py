from flask_restful import abort

from ..models.users import User
from ..models.chats import Chat


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