
from flask_socketio import join_room
from flask_login import current_user

# from flask_socketio import send

from flask_app.extensions import db_constants


def register_events(socket_io):

    @socket_io.on('subscribe_tracker_data', namespace='/tracker')
    def subscribe_tracker_data():
        if not current_user.is_authenticated:
            return
        join_room(db_constants.eye_trackers_socketio_room)
