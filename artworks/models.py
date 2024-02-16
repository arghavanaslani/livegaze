from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy import func
from extensions.base_model import Base


class Artwork(Base):
    __tablename__ = "Artwork"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    bio = Column(Text)
    tag_id = Column(Integer, unique=True)
    data_added = Column(DateTime, default=func.now())
    image_path = Column(String(256))
    # gaze_datas: Mapped[List["GazeData"]] = relationship(back_populates='artwork')
