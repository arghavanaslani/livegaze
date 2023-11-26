import os
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)




