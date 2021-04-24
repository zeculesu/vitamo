from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relation
from sqlalchemy_serializer import SerializerMixin

from ..db_session import SQLAlchemyBase


user_to_message = Table('user_to_message', SQLAlchemyBase.metadata,
                        Column('user', Integer, ForeignKey('users.id')),
                        Column('message', Integer, ForeignKey('messages.id')))


class Message(SQLAlchemyBase, SerializerMixin):
    __tablename__ = 'messages'

    serialize_fields = ('id', 'text', 'chat_id', 'current_chat_id',
                        'sender.id', 'sender.username', 'sender.chats'
                        'attachments', 'is_read', 'is_edited', 'sent_time')

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(String, nullable=True)
    sender = Column(Integer, ForeignKey('users.id'), nullable=True)
    sender_obj = relation('User', foreign_keys=sender)
    chat_id = Column(Integer, ForeignKey('chats.id'))
    current_chat_id = Column(Integer, ForeignKey('chats.id'), default=chat_id)
    chat = relation('Chat', foreign_keys=current_chat_id)
    attachments = relation('Attachment')
    viewable_for = relation('User', secondary='user_to_message', backref='messages')
    is_read = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    sent_time = Column(DateTime, default=datetime.now)

    def to_dict(self, only=(), rules=(),
                date_format=None, datetime_format=None, time_format=None, tzinfo=None,
                decimal_format=None, serialize_types=None):
        only = only if only else self.serialize_fields
        return SerializerMixin.to_dict(self, only, rules, date_format, datetime_format,
                                       time_format, tzinfo, decimal_format, serialize_types)


if __name__ == '__main__':
    message = Message()
