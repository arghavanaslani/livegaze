from sqlalchemy import Column, Integer, DateTime, String, Enum
from flask_app.extensions.base_model import Base
from sqlalchemy.sql import func
import enum


class TrackerState(enum.Enum):
    inactive = 0
    ready = 1
    sending_data = 2

class Tracker(Base):
    __tablename__ = "Tracker"
    id = Column(Integer, primary_key=True)
    tracker_id = Column(String, nullable=False)
    added_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    # board_id = Column(ForeignKey('Board.id'))
    tracker_state = Column(Enum(TrackerState), default=TrackerState.inactive)