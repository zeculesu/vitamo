from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relation

from ..db_session import SQLAlchemyBase


class Message(SQLAlchemyBase):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(String, nullable=True)
    sender = Column(Integer, ForeignKey('users.id'))
    attachments = relation('Attachment', back_populates='message')
    viewable_for = relation('User', back_populates='message')
    sent_time = Column(DateTime, default=datetime.now)


if __name__ == '__main__':
    message = Message()
