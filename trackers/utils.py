from trackers.models import Tracker, TrackerState
from extensions import socket_io
from extensions import db_constants


def reset_tracker_states(db):
    """
    Reset the states of all trackers in the database to inactive.
    """
    trackers = db.session.query(Tracker).all()
    for tracker in trackers:
        tracker.tracker_state = TrackerState.inactive
        socket_io.socket_io.emit('update_tracker_status',
                                  {'tracker_id': tracker.tracker_id, 'tracker_status': TrackerState.inactive},
                                  namespace='/tracker', room=db_constants.eye_trackers_socketio_room)
    db.session.commit()


def updated_tracker_state(tracker_id, tracker_state):
    socket_io.socket_io.emit('update_tracker_status',
                              {'tracker_id': tracker_id, 'tracker_status': tracker_state.value},
                              namespace='/tracker', room=db_constants.eye_trackers_socketio_room)