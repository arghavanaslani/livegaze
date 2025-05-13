from flask import Blueprint, render_template
from .models import Tracker
from flask_app.extensions.db_config import db

trackers_blueprint = Blueprint('trackers', __name__, url_prefix='/trackers')


@trackers_blueprint.route('/')
def trackers_list():
    trackers = db.session.query(Tracker).all()
    return render_template('trackers/trackers_list.html', trackers=trackers)

