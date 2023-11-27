from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, Enum
from extensions.base_model import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
import enum

class GazeType(enum):
    simple = 0
    torch = 1


class GazeData(Base):
    __tablename__ = "GazeData"
    id = Column(Integer, primary_key=True)
    added_date = Column(DateTime, server_default=func.now())
    artwork_id = Column(ForeignKey('Artwork.id'))
    gaze_type = Column(Enum(GazeType))
    eyetracker_id = Column(Integer, nullable=False)
    gaze_position_x = Column(Float, nullable=False)
    gaze_position_y = Column(Float, nullable=False)
    # artwork: [Mapped["Artwork"]] = relationship(back_populates='gaze_datas')