from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Table, ForeignKey
from sqlalchemy.orm import relation
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..db_session import SQLAlchemyBase

chat_to_user = Table('chat_to_user', SQLAlchemyBase.metadata,
                     Column('chat', Integer, ForeignKey('chats.id')),
                     Column('users', Integer, ForeignKey('users.id')))


class User(SQLAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    username = Column(String)
    chats = relation('Chat', secondary='chat_to_user', backref='users')
    created_date = Column(DateTime, default=datetime.now)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
