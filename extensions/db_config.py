from flask_sqlalchemy import SQLAlchemy
from extensions.base_model import Base

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    from artworks.models import Artwork
    from gaze_manager.models import GazeDatabaseModel
    with app.app_context():
        Base.metadata.create_all(db.engine)
        db.create_all()
        db.session.commit()




