from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relation
from sqlalchemy_serializer import SerializerMixin

from ..db_session import SQLAlchemyBase

messages_to_chat = Table('messages_to_chat', SQLAlchemyBase.metadata,
                         Column('messages', Integer, ForeignKey('messages.id')),
                         Column('chats', Integer, ForeignKey('chats.id')))


class Chat(SQLAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    serialize_fields = ('id', 'title', 'logo',
                        'users.id', 'users.username',
                        'users.chats.id', 'users.chats.title', 'users.chats.logo',
                        'messages.id',
                        'messages.sender.id', 'messages.sender.username', 'messages.sender.logo',
                        'messages.text', 'messages.is_read', 'messages.is_edited', 'messages.sent_time')

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String, nullable=True)
    logo = Column(Integer, ForeignKey('attachments.id'), nullable=True)
    messages = relation('Message', secondary='messages_to_chat', backref='chats')

    def to_dict(self, only=(), rules=(),
                date_format=None, datetime_format=None, time_format=None, tzinfo=None,
                decimal_format=None, serialize_types=None):
        only = only if only else self.serialize_fields
        return SerializerMixin.to_dict(self, only, rules, date_format, datetime_format,
                                       time_format, tzinfo, decimal_format, serialize_types)
