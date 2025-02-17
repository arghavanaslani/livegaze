import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy import func
from extensions.base_model import Base


class Board(Base):
    __tablename__ = "Board"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    bio = Column(Text)
    tag_id = Column(Integer, unique=True)
    data_added = Column(DateTime, default=func.now())
    image_path = Column(String(256))
    # gaze_datas: Mapped[List["GazeData"]] = relationship(back_populates='artwork')


class StimType(enum.Enum):
    IMAGE = 0
    VIDEO = 1

class Stimulus(Base):
    __tablename__ = "Stimulus"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    data_added = Column(DateTime, default=func.now())
    file_path = Column(String(256))
    stim_type = Column(Enum(StimType))