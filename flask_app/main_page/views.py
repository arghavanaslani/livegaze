from flask import Blueprint, render_template, Response
from flask_login import login_required
from flask_app.boards.models import Board
from flask_app.gaze_manager.models import GazeDataSession
from flask_app.extensions.db_config import db, redis_client
from flask_app.extensions import redis_constants

main_page_blueprint = Blueprint('main_page', __name__)


@main_page_blueprint.route('/')
@login_required
def index():
    paintings = db.session.query(Board).all()
    return render_template('main_page.html', boards=[{"id": painting.id , "stimuli": [stimulus.stimulus for stimulus in painting.stimuli],
                                                      "name": painting.name} for painting in paintings])

@main_page_blueprint.route('/toggle_record', methods=['POST'])
@login_required
def toggle_record():
    record = redis_client.get(redis_constants.RECORD)
    record = redis_constants.is_recording(record)
    if record:
        redis_client.set(redis_constants.RECORD, 'False')
        return Response('Recording stopped', 200)
    else:
        redis_client.set(redis_constants.RECORD, 'True')
        # create gazeDataSession
        gaze_data_session = GazeDataSession()
        db.session.add(gaze_data_session)
        db.session.commit()
        redis_client.set(redis_constants.RECORD_SESSION_ID, gaze_data_session.id)
        return Response('Recording started', 200)


@main_page_blueprint.route('/is_recording', methods=['GET'])
@login_required
def is_recording():
    record = redis_client.get(redis_constants.RECORD)
    record = redis_constants.is_recording(record)
    return Response(str(record), 200)