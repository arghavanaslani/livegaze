from flask_login import UserMixin

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func

from flask_app.extensions.base_model import Base


class User(Base, UserMixin):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=True)
    password_hash = Column(String(128))
    date_added = Column(DateTime, default=func.now())




