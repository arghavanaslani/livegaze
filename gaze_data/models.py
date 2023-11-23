from sqlalchemy import Column, Integer, Float,ForeignKey, DateTime
from extensions.base_model import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class GazeData(Base):
    __tablename__ = "GazeData"
    id = Column(Integer, primary_key=True)
    added_date = Column(DateTime, server_default=func.now())
    artwork_id = Column(ForeignKey('Artwork.id'))
    eyetracker_id = Column(Integer, nullable=False)
    gaze_position_x = Column(Float, nullable=False)
    gaze_position_y = Column(Float, nullable=False)
    artwork = relationship(back_populates='gaze_datas')