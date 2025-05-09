from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, Enum
from extensions.base_model import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class GazeType(enum.Enum):
    simple = 1
    torch = 2

class GazeData:
    def __init__(self, camera_id: str, timestamp: float, x: float, y: float, stim_id: int):
        self.camera_id: str = camera_id
        self.stim_id: int = stim_id
        self.timestamp: float = timestamp
        self.pos_x: float = x
        self.pos_y: float = y


class GazeDatabaseModel(Base):
    __tablename__ = "GazeData"
    id = Column(Integer, primary_key=True)
    added_date = Column(DateTime, server_default=func.now())
    board_id = Column(ForeignKey('Board.id'))
    session_id = Column(ForeignKey('GazeDataSession.id'))
    gaze_type = Column(Enum(GazeType))
    eyetracker_id = Column(String, nullable=False)
    gaze_position_x = Column(Float, nullable=False)
    gaze_position_y = Column(Float, nullable=False)
    # artwork: [Mapped["Artwork"]] = relationship(back_populates='gaze_datas')
    session = relationship("GazeDataSession", back_populates="gaze_datas")

    def __init__(self, gaze_data: GazeData, **kw):
        super().__init__(**kw)
        self.added_date = datetime.fromtimestamp(gaze_data.timestamp)
        self.board_id = gaze_data.stim_id
        self.gaze_type = GazeType.simple
        self.eyetracker_id = gaze_data.camera_id
        self.gaze_position_x = gaze_data.pos_x
        self.gaze_position_y = gaze_data.pos_y


class GazeDataSession(Base):
    __tablename__ = "GazeDataSession"
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, server_default=func.now())
    gaze_datas = relationship("GazeDatabaseModel", back_populates="session")

