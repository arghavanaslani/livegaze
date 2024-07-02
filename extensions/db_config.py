from flask_sqlalchemy import SQLAlchemy
from extensions.base_model import Base
from flask_redis import FlaskRedis
from flask import Flask
from extensions.redis_constants import TRACKERS_SET

db = SQLAlchemy()

redis_client = FlaskRedis()


def init_db(app):
    db.init_app(app)
    redis_client.init_app(app)
    #remove the set from redis
    redis_client.delete(TRACKERS_SET)
    from artworks.models import Artwork
    from gaze_manager.models import GazeDatabaseModel
    with app.app_context():
        Base.metadata.create_all(db.engine)
        db.create_all()
        db.session.commit()




