from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relation

from ..db_session import SQLAlchemyBase


class Message(SQLAlchemyBase):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text = Column(String, nullable=True)
    sender = Column(Integer, ForeignKey('users.id'))
    attachments = relation('Attachment')
    # viewable_for = relation('User', back_populates='message')
    is_read = Column(Boolean, default=False)
    sent_time = Column(DateTime, default=datetime.now)


if __name__ == '__main__':
    message = Message()
