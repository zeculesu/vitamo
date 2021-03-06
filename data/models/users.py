from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, DateTime, Table, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..db_session import SQLAlchemyBase

chat_to_user = Table('chat_to_user', SQLAlchemyBase.metadata,
                     Column('chat', Integer, ForeignKey('chats.id')),
                     Column('users', Integer, ForeignKey('users.id')))

user_to_user = Table('user_to_user', SQLAlchemyBase.metadata,
                     Column('user1', Integer, ForeignKey('users.id')),
                     Column('user2', Integer, ForeignKey('users.id')))


class User(SQLAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'users'

    serialize_fields = ('id', 'email', 'username',
                        'description', 'logo',
                        'chats.id', 'chats.title', 'chats.logo',
                        'chats.users.id', 'chats.users.username',
                        'created_date')

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    username = Column(String)
    description = Column(String, nullable=True)
    logo = Column(String, nullable=True)
    # contacts = relation('User', secondary='user_to_user', backref='users')
    chats = relation('Chat', secondary='chat_to_user', backref='users')
    created_date = Column(DateTime, default=datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def to_dict(self, only=(), rules=(),
                date_format=None, datetime_format=None, time_format=None, tzinfo=None,
                decimal_format=None, serialize_types=None):
        only = only if only else self.serialize_fields
        return SerializerMixin.to_dict(self, only, rules, date_format, datetime_format, time_format,
                                       tzinfo, decimal_format, serialize_types)
