from flask_login import UserMixin

import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy import func, text
from sqlalchemy.orm import relationship

from extensions.base_model import Base


class User(Base, UserMixin):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True)
    password_hash = Column(String(128))
    date_added = Column(DateTime, default=func.now())




