
from flask_socketio import join_room, send, emit
from flask_login import current_user

# from flask_socketio import send

from gaze_manager import gaze_manager
from extensions.db_config import redis_client, db
from extensions import db_constants
import json


def register_events(socket_io):

    @socket_io.on('subscribe_tracker_data', namespace='/tracker')
    def subscribe_tracker_data():
        if not current_user.is_authenticated:
            return
        join_room(db_constants.eye_trackers_socketio_room)
