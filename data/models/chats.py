from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relation

from ..db_session import SQLAlchemyBase

messages_to_chat = Table('messages_to_chat', SQLAlchemyBase.metadata,
                         Column('messages', Integer, ForeignKey('messages.id')),
                         Column('chats', Integer, ForeignKey('chats.id')))


class Chat(SQLAlchemyBase):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String, nullable=True)
    logo = Column(Integer, ForeignKey('media.id'), nullable=True)
    users = relation('User', secondary='chats_to_user', backref='chats')
    messages = relation('Message', secondary='messages_to_chat', backref='chats')
