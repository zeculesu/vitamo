from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relation

from ..db_session import SQLAlchemyBase


class Attachment(SQLAlchemyBase):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    attachment_type = Column(String, nullable=True)
    message = Column(Integer, ForeignKey('messages.id'))
    url = Column(String)
