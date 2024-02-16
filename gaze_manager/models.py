from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, Enum
from extensions.base_model import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
import enum


class GazeType(enum.Enum):
    simple = 1
    torch = 2


class GazeDatabaseModel(Base):
    __tablename__ = "GazeData"
    id = Column(Integer, primary_key=True)
    added_date = Column(DateTime, server_default=func.now())
    artwork_id = Column(ForeignKey('Artwork.id'))
    gaze_type = Column(Enum(GazeType))
    eyetracker_id = Column(Integer, nullable=False)
    gaze_position_x = Column(Float, nullable=False)
    gaze_position_y = Column(Float, nullable=False)
    # artwork: [Mapped["Artwork"]] = relationship(back_populates='gaze_datas')


class GazeData:
    def __init__(self, camera_id: int, timestamp: int, pos_x: float, pos_y: float, stim_id: int):
        self.camera_id: int = camera_id
        self.stim_id: int = stim_id
        self.timestamp: int = timestamp
        self.pos_x: float = pos_x
        self.pos_y: float = pos_y
