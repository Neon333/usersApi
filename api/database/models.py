from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime

from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=255), nullable=False, unique=True, index=True)
    email = Column(String(length=255), nullable=False, unique=True, index=True)
    register_date = Column(DateTime, server_default=func.now())
    password = Column(String(length=255), nullable=False)
