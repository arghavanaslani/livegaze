from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from typing import List
from extensions.base_model import Base


class Artwork(Base):
    __tablename__ = "Artwork"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    bio = Column(Text)
    image_path = Column(String(256))
    # gaze_datas: Mapped[List["GazeData"]] = relationship(back_populates='artwork')
