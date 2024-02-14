from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey

from extensions.base_model import Base


class Settings(Base):
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True)
    pointer_id = Column(Integer, default=0)
    pointer_size = Column(Float, default=0.5)
